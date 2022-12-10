import asyncio
from rq import Queue
import sqlalchemy as sa
from aia.agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from dbs.vector_utils import tokenize_string
from indexers.utils.extract_document_type import extract_document_type
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner
from indexers.utils.extract_document_citing_slavery_summary import extract_document_citing_slavery_summary
from indexers.utils.extract_document_citing_slavery_summary_one_liner import extract_document_citing_slavery_summary_one_liner
from models.ocr import split_file_pdf_to_pil, ocr_parse_image_text


async def _index_pdf_process_content(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_pdf_process_content) started", document_id)
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    file = files_query.scalars().first()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()

    if len(document_content) == 0:
        # 1. PDF OCR -> TEXT (SENTENCES) / IMAGES
        print(f"INFO (index_pdf.py:_index_pdf_process_content): converting {file.filename} to pngs")
        pdf_image_files = split_file_pdf_to_pil(file)

        # 2. DOCUMENT CONTENT CREATE
        # --- 2a. Process text for all pages
        # # # V2 ASYNC w/ PARALLEL PROCESSORS USING RAY (not threads)
        # # HOLY F. On my laptop, doing a 38 page PDF took 5+ minutes. This takes seconds now bc its just async web requests
        # @ray.remote
        # def process_page_text(pdf_image_file):
        #     return ocr_parse_image_text(pdf_image_file)
        # pages_text_futures = list(map(lambda file: process_page_text.remote(file), pdf_image_files))
        # pages_text = ray.get(pages_text_futures)
        # # V3 ASYNC w/ PARALLEL JOBS USING RQ (at sync speed, but will get fast w/ multiple instances)
        # page_text_jobs = indexing_queue.enqueue_many(
        #     map(lambda file: Queue.prepare_data(func=job_ocr_parse_image_text, args=[file]), pdf_image_files)
        # )
        # pages_text = await_enqueued_results(page_text_jobs)
        # V4 ASYNC COROUTINES
        # --- tasks
        pages_text_coroutines = map(lambda pdf_image_file: ocr_parse_image_text(pdf_image_file), pdf_image_files)
        print(f'INFO (index_pdf.py:_index_pdf_process_content): coroutines', pages_text_coroutines)
        # --- results
        pages_text = await asyncio.gather(*pages_text_coroutines)
        print(f'INFO (index_pdf.py:_index_pdf_process_content): pages_text', pages_text)
        
        # --- 2b. Tokenize/process text by sentence
        document_content_sentences = []
        for idx, page_text in enumerate(pages_text):
            page_ocr_text_sentences = tokenize_string(page_text, "sentence")
            document_content_sentences += list(map(lambda sentence: DocumentContent(
                document_id=document_id,
                page_number=str(idx + 1), # wtf this was throwing this whole time but only when i commit right after did it show up?????
                text=sentence,
                tokenizing_strategy="sentence"
            ), page_ocr_text_sentences))
        session.add_all(document_content_sentences)

        # --- 2c. Tokenize/process text by max_size (defined by text-similiarty-davinci-001, should later try chunking by # sentences)
        document_text = " ".join(map(lambda content: content.text, document_content_sentences))
        document_text_chunks = tokenize_string(document_text, "max_size")
        document_content_text = list(map(lambda chunk: DocumentContent(
            document_id=document_id,
            text=chunk,
            tokenizing_strategy="max_size"
        ), document_text_chunks))
        session.add_all(document_content_text)
        print(f"INFO (index_pdf.py:_index_pdf_process_content): Inserted new document content records")
    else:
        print(f"INFO (index_pdf.py:_index_pdf_process_content): already processed content for document #{document_id} (content count: {len(document_content)})")

    # 3. SAVE
    document.status_processing_content = "completed"
    session.add(document) # if modifying a record/model, we can use add() to do an update
    print('INFO (index_pdf.py:_index_pdf_process_content): done')

async def _index_pdf_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): start')
    # SETUP
    # --- documents
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = list(document_content_query.scalars().all())
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): # of document content', len(document_content))
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == "sentence", document_content))
    document_content_maxed_size = list(filter(lambda c: c.tokenizing_strategy == "max_size", document_content))
    # V2 CREATE EMBEDDINGS
    # --- session/agent
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id)
    aiagent_max_size_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_max_size_embed, case_id=document.case_id)
    # --- sentences (sentence-transformer = free, but very limited token length)
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): encoding sentences...', document_content_sentences)
    sentence_embeddings = aiagent_sentence_embeder.encode_text(list(map(lambda c: c.text, document_content_sentences)))
    sentence_embeddings_as_models = []
    for index, embedding in enumerate(sentence_embeddings):
        sentence_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_sentences[index].id,
            encoded_model_engine=aiagent_sentence_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
        ))
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): encoded sentences...')
    session.add_all(sentence_embeddings_as_models)
    # --- max_size (gtp3 ada = very very cheap, and large token length)
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): encoding max_size...', document_content_maxed_size)
    maxed_size_embeddings = aiagent_max_size_embeder.encode_text(list(map(lambda c: c.text, document_content_maxed_size)))
    maxed_size_embeddings_as_models = []
    for index, embedding in enumerate(maxed_size_embeddings):
        maxed_size_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_maxed_size[index].id,
            encoded_model_engine=aiagent_max_size_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(),
        ))
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): encoded max_size...')
    session.add_all(maxed_size_embeddings_as_models)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)
    print('INFO (index_pdf.py:_index_pdf_process_embeddings): done')

async def _index_pdf_process_extractions(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_pdf_process_extractions): start')
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(
        sa.select(DocumentContent)
            .where(DocumentContent.document_id == document_id)
            .where(DocumentContent.tokenizing_strategy == "sentence"))
    document_content_sentences = document_content_query.scalars()
    document_content_text = " ".join(map(lambda content: content.text, document_content_sentences))
    print('INFO (index_pdf.py:_index_pdf_process_extractions): len(document_text) = {length}'.format(length=len(document_content_text)))
    use_repeat_methods = len(document_content_text) > 11_000 # 4097 tokens allowed, but a token represents 3 or 4 characters
    print('INFO (index_pdf.py:_index_pdf_process_extractions): use_repeat_methods = {bool}'.format(bool=use_repeat_methods))
    # EXTRACT
    # --- classification/description
    print('INFO (index_pdf.py:_index_pdf_process_extractions): document_description')
    document.document_description = extract_document_type(document_content_text)
    # --- summary
    print('INFO (index_pdf.py:_index_pdf_process_extractions): document_summary')
    if len(document_content_text) < 250_000:
        document.document_summary = extract_document_summary(document_content_text)
        document.document_summary_one_liner = extract_document_summary_one_liner(document.document_summary)
        # HACK: just putting this here for citing slavery/access case law test
        if 'slave' in document_content_text:
            document.document_citing_slavery_summary = extract_document_citing_slavery_summary(document_content_text)
            document.document_citing_slavery_summary_one_liner = extract_document_citing_slavery_summary_one_liner(document.document_citing_slavery_summary)
    else:
        print('INFO (index_pdf.py:_index_pdf_process_extractions): document is too long')
    # --- cases/laws mentioned
    #  TODO: await extract_document_caselaw_mentions(document_content_text)
    # --- event timeline v2
    document.document_events = await extract_document_events_v1(document_content_text)
    # --- organizations mentioned
    #  TODO: await extract_document_organizations(document_content_text)
    # --- people mentioned + context within document
    #  TODO: await extract_document_people(document_content_text)
    # --- SAVE
    document.status_processing_extractions = "completed"
    session.add(document)
    print('INFO (index_pdf.py:_index_pdf_process_extractions): done')


# INDEX_PDF
async def index_pdf(session, document_id) -> int:
    print(f"INFO (index_pdf.py): indexing document #{document_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_pdf.py): processing document #{document_id} content")
        await _index_pdf_process_content(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): processing document #{document_id} embeddings")
        await _index_pdf_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): processing document #{document_id} extractions")
        await _index_pdf_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_pdf.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_pdf.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
