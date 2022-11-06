import asyncio
import easyocr
import io
import numpy
import openai
from pdf2image import convert_from_bytes, convert_from_path
import pickle
import textwrap
from time import sleep

from sqlalchemy import insert, select, update

from env import env_get_open_ai_api_key
from gideon_faiss import index_documents_add_text, index_sentences_add_text
from gideon_gpt import gpt_completion, gpt_completion_repeated, gpt_edit, gpt_embedding, gpt_summarize, gpt_vars
from gideon_utils import filter_empty_strs, get_file_path, open_txt_file, tokenize_string
from models import Document, DocumentContent, File
from s3_utils import s3_get_file_bytes, s3_get_file_url, s3_upload_file

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()
# --- OCR
reader = easyocr.Reader(['en'], gpu=False, verbose=True) # don't think we'll have GPUs on AWS instances

async def _index_pdf_process_file(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_pdf_process_file) started", document_id)
    document_query = await session.execute(select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    # STATUS
    files_query = await session.execute(select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    print(f"INFO (index_pdf.py:_index_pdf_process_file) ##TODO## files")
    file = files.first()
    file_bytes = s3_get_file_bytes(file.upload_key)
    # PDF OCR -> TEXT (SENTENCES) / IMAGES
    # --- thinking up front we deconstruct into sentences bc it's easy to build up into other sizes/structures from that + meta data
    print(f"INFO (index_pdf.py:_index_pdf_process_file): fetching document's documentcontent")
    document_content_query = await session.execute(select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all() # .all() will turn ScalarResult into a list()
    print(f"INFO (index_pdf.py:_index_pdf_process_file): fetched document's documentcontent (length: {len(document_content)})")
    if len(document_content) == 0:
        # CONVERT (PDF -> Image[] for OCR)
        print(f"INFO (index_pdf.py:_index_pdf_process_file): converting {file.filename} to pngs")
        # PDF -> PNGs args
        # https://github.com/Belval/pdf2image#whats-new
        pdf_image_files = convert_from_bytes(file_bytes, fmt='png', size=(1400, None)) # always ensure max size to limit processing OCR demand
        print(f"INFO (index_pdf.py:_index_pdf_process_file): converted {file.filename} to ##TODO## pngs")
        # PER PAGE (get text)
        for idx, pdf_image_file in enumerate(pdf_image_files): # FYI can't unpack err happens on pages, so we cast w/ enumerate to add in an index
            page_number = idx + 1
            tokenizing_strategy = "sentence"
            print('INFO (index_pdf.py:_index_pdf_process_file): page {page_number}'.format(page_number=page_number), pdf_image_file)
            # --- ocr (confused as shit converting PIL.PngImagePlugin.PngImageFile to bytes)
            img_byte_arr = io.BytesIO()
            pdf_image_file.save(img_byte_arr, format='png')
            print('INFO (index_pdf.py:_index_pdf_process_file): page {page_number} OCRing'.format(page_number=page_number), pdf_image_file)
            page_ocr_str_array = reader.readtext(img_byte_arr.getvalue(), detail=0)
            # --- compile all extracted text tokens into 1 big string so we can break down into sentences
            page_ocr_text = ' '.join(page_ocr_str_array).encode(encoding='ASCII',errors='ignore').decode() # safe string
            print('INFO (index_pdf.py:_index_pdf_process_file): page {page_number} ocr = "{page_ocr_text}"'.format(page_number=page_number, page_ocr_text=page_ocr_text))
            # --- for each page, break down into sentences for content array
            page_ocr_text_sentences = tokenize_string(page_ocr_text, tokenizing_strategy)
            print(f"INFO (index_pdf.py:_index_pdf_process_file): tokenized page {page_number}", page_ocr_text_sentences)
            # --- prep document content for page
            session.add_all(
                list(map(lambda sentence: DocumentContent(
                    document_id=document_id,
                    page_number=str(page_number), # wtf this was throwing this whole time but only when i commit right after did it show up?????
                    text=sentence,
                    tokenizing_strategy=tokenizing_strategy
                ), page_ocr_text_sentences))
            )
        print(f"INFO (index_pdf.py:_index_pdf_process_file): Inserted new document content records")
    # --- save
    document.status_processing_files = "completed"
    session.add(document) # if modifying a record/model, we can use add() to do an update

async def _index_pdf_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): start')
    document_query = await session.execute(select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): document content', document_content)
    document_content_text = " ".join(map(lambda content: content.text, document_content))
    # 1) large embeddings for summarization
    document_content_text_chunks = textwrap.wrap(document_content_text, 3_500)
    for chunk in document_content_text_chunks:
        # --- add to index (handles embedding creation)
        await index_documents_add_text(session=session, text=chunk, document_id=document_id)
        # --- take a break (throttled by openai 60 reqs/min)
        sleep(1.5)
    # 2) sentence embeddings for location look ups
    for content in list(filter(lambda content: content.tokenizing_strategy == "sentence", document_content)):
        # --- add to index (handles embedding creation)
        await index_sentences_add_text(session=session, text=content.text, document_content_id=content.id)
        # --- take a break (throttled by openai 60 reqs/min)
        sleep(1.5)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)

async def _index_pdf_process_extractions(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_pdf_process_extractions): start')
    document_query = await session.execute(select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars()
    document_content_text = " ".join(map(lambda content: content.text, document_content))
    # VARS
    # --- docs: summaries
    document_description = ''
    document_summary = ''
    # --- docs: extractions
    event_timeline = []
    mentions_people = []
    people = {}
    print('INFO (index_pdf.py:_index_pdf_process_extractions): len(document_text) = {length}'.format(length=len(document_content_text)))
    use_repeat_methods = len(document_content_text) > 11_000 # 4097 tokens allowed, but a token represents 3 or 4 characters
    print('INFO (index_pdf.py:_index_pdf_process_extractions): use_repeat_methods = {bool}'.format(bool=use_repeat_methods))
    # EXTRACT
    # --- classification/description
    print('INFO (index_pdf.py:_index_pdf_process_extractions): document_description')
    if len(document_description) == 0:
        document_description = gpt_completion(
            open_txt_file(get_file_path('./prompts/prompt_document_type.txt')).replace('<<SOURCE_TEXT>>', document_content_text[0:11_000]),
            max_tokens=75
        )
    else:
        print('INFO (index_pdf.py:_index_pdf_process_extractions): document_description exists')
    # --- summary
    print('INFO (index_pdf.py:_index_pdf_process_extractions): document_summary')
    if len(document_summary) == 0 and len(document_content_text) < 250_000:
        document_summary = gpt_summarize(document_content_text)
    else:
        print('INFO (index_pdf.py:_index_pdf_process_extractions): document_summary exists or document is too long')
    # --- cases/laws mentioned
    # print('INFO (index_pdf.py:_index_pdf_process_extractions): mentions_cases_laws')
    # if len(document_content_text) < 250_000:
    #     if use_repeat_methods == True:
    #         mentions_cases_laws_dirty = gpt_completion_repeated(open_txt_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')),document_content_text,text_chunk_size=11_000,return_list=True)
    #     else:
    #         mentions_cases_laws_dirty = gpt_completion(open_txt_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')).replace('<<SOURCE_TEXT>>',document_content_text))
    #     mentions_cases_laws = filter_empty_strs(gpt_edit(
    #         open_txt_file(get_file_path('./prompts/edit_clean_list.txt')),
    #         '\n'.join(mentions_cases_laws_dirty) if use_repeat_methods == True else mentions_cases_laws_dirty # join linebreaks if we have a list
    #     ).split('\n'))
    # else:
    #     print('INFO (index_pdf.py:_index_pdf_process_extractions): mentions_cases_laws skipped because document text is too long')
    # # --- if a discovery document (ex: police report, testimony, motion)
    # if is_discovery_document == True:
    # --- event timeline (split on linebreaks, could later do structured parsing prob of dates)
    # print('INFO (index_pdf.py:_index_pdf_process_extractions): event_timeline')
    # if use_repeat_methods == True:
    #     event_timeline_dirty = gpt_completion_repeated(open_txt_file(get_file_path('./prompts/prompt_timeline.txt')),document_content_text,text_chunk_size=11_000,return_list=True)
    # else:
    #     event_timeline_dirty = gpt_completion(open_txt_file(get_file_path('./prompts/prompt_timeline.txt')).replace('<<SOURCE_TEXT>>',document_content_text))
    # event_timeline = filter_empty_strs(gpt_edit(
    #     open_txt_file(get_file_path('./prompts/edit_event_timeline.txt')),
    #     '\n'.join(event_timeline_dirty) if use_repeat_methods == True else event_timeline_dirty # join linebreaks if we have a list
    # ).split('\n'))
    # --- organizations mentioned
    # print('INFO (index_pdf.py:_index_pdf_process_extractions): mentions_organizations')
    # if use_repeat_methods == True:
    #     mentions_organizations_dirty = gpt_completion_repeated(open_txt_file(get_file_path('./prompts/prompt_mentions_organizations.txt')),document_content_text,text_chunk_size=11_000,return_list=True)
    # else:
    #     mentions_organizations_dirty = gpt_completion(open_txt_file(get_file_path('./prompts/prompt_mentions_organizations.txt')).replace('<<SOURCE_TEXT>>',document_content_text))
    # mentions_organizations = filter_empty_strs(gpt_edit(
    #     open_txt_file(get_file_path('./prompts/edit_clean_list.txt')),
    #     '\n'.join(mentions_organizations_dirty) if use_repeat_methods == True else mentions_organizations_dirty # join linebreaks if we have a list
    # ).split('\n'))
    # --- people mentioned + context within document
    # print('INFO (index_pdf.py:_index_pdf_process_extractions): mentions_people')
    # if use_repeat_methods == True:
    #     mentions_people_dirty = gpt_completion_repeated(open_txt_file(get_file_path('./prompts/prompt_mentions_people.txt')),document_content_text,text_chunk_size=11_000,return_list=True)
    # else:
    #     mentions_people_dirty = gpt_completion(open_txt_file(get_file_path('./prompts/prompt_mentions_people.txt')).replace('<<SOURCE_TEXT>>',document_content_text))
    # mentions_people = filter_empty_strs(gpt_edit(
    #     open_txt_file(get_file_path('./prompts/edit_clean_names_list.txt')),
    #     '\n'.join(mentions_people_dirty) if use_repeat_methods == True else mentions_people_dirty # join linebreaks if we have a list
    # ).split('\n'))
    # TODO: skipping follow ups on people bc it takes forever atm. faster dev cycle plz
    # print('INFO (index_pdf.py:_index_pdf_process_extractions): mentions_people #{num_people}'.format(num_people=len(mentions_people)))
    # for name in mentions_people:
    #     # TODO: need to build a profile by sifting through the full doc, not just initial big chunk
    #     people[name] = gpt_completion(open_txt_file(get_file_path('./prompts/prompt_mention_involvement.txt')).replace('<<SOURCE_TEXT>>', document_content_text[0:11_000]).replace('<<NAME>>',name), max_tokens=400)
    # --- SAVE
    document.document_description=document_description
    document.document_summary=document_summary
    session.add(document)


# INDEX_PDF
async def index_pdf(session, pyfile):
    print(f"INFO (index_pdf.py): indexing {pyfile.name} ({pyfile.type})")
    # SETUP DOCUMENT
    document_query = await session.execute(
        insert(Document)
            .values(status_processing_files="queued")
            .returning(Document.id)) # can't seem to return anything except id
    document_id = document_query.scalar_one_or_none()
    print(f"INFO (index_pdf.py): index_document id {document_id}")
    
    # SAVE & RELATE FILE
    filename = pyfile.name
    upload_key = pyfile.name # TODO: avoid collisions w/ unique prefix
    # --- save to S3
    s3_upload_file(upload_key, pyfile)
    # --- create File()
    input_s3_url = s3_get_file_url(filename)
    session.add(
        insert(File).values(
            filename=pyfile.name,
            mime_type=pyfile.type,
            upload_key=upload_key,
            upload_url=input_s3_url,
            document_id=document_id
        ))
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_pdf.py): processing file", upload_key)
        await _index_pdf_process_file(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): processing embeddings", upload_key)
        await _index_pdf_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): processing extractions", upload_key)
        await _index_pdf_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): finished intake of document #{document_id}")
        # SAVE/COMMIT
        # this happens by the context/caller of this func
    except Exception as err:
        print(f"ERROR (index_pdf.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
