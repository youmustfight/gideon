from time import sleep
import easyocr
import io
import json
from env import env_get_open_ai_api_key
from gideon_utils import filter_empty_strs, get_file_path, open_txt_file
from gideon_gpt import gpt_completion, gpt_completion_repeated, gpt_edit, gpt_embedding, gpt_summarize
import openai
import os
from pdf2image import convert_from_path # FYI, on Mac -> brew install poppler
import textwrap

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()
# --- OCR
reader = easyocr.Reader(['en'])

# INDEX_PDF
def index_pdf(filename, index_type):
    print('INFO (index_pdf.py): started')
    # FILE + PROPERTIES (w/ OCR)
    is_discovery_document = index_type == "discovery"
    input_filepath = get_file_path('../documents/{filename}'.format(filename=filename))
    output_filepath = get_file_path('../indexed/{filename}.json'.format(filename=filename))
    # --- docs: all
    document_text = '' # string
    document_text_vectors = [] # { text, vector }[]
    document_text_by_page = [] # string[]
    document_text_vectors_by_page = [] # { text, vector, page_number }[]
    document_text_vectors_by_paragraph = [] # { text, vector, page_number }[]
    document_text_vectors_by_sentence = [] # { text, vector, page_number }[]
    document_type = ''
    document_summary = ''
    # --- docs: discovery
    event_timeline = []
    mentions_cases_laws = []
    mentions_organizations = []
    mentions_people = []
    people = {}
    if os.path.isfile(output_filepath) == True:
        # SKIP OCR IF WE HAVE DOCUMENT/PAGE TEXT
        existing_data = json.load(open(output_filepath))
        document_text = existing_data['document_text']
        document_text_by_page = existing_data['document_text_by_page']
        try:
            if existing_data['document_type'] != None and len(existing_data['document_type']) > 0:
                document_type = existing_data['document_type']
        except:
            print('INFO (index_pdf.py): no existing document type')
        try:
            if existing_data['document_summary'] != None and len(existing_data['document_summary']) > 0:
                document_summary = existing_data['document_summary']
        except:
            print('INFO (index_pdf.py): no existing document summary')
    else:
        # CONVERT (PDF -> Image[] for OCR)
        print('INFO (index_pdf.py): converting {convert_file_path}'.format(convert_file_path=input_filepath))
        pdf_image_files = convert_from_path(input_filepath, fmt='png')
        print('INFO (index_pdf.py): converted {convert_file_path}'.format(convert_file_path=input_filepath))
        # PER PAGE (get text)
        for idx, pdf_image_file in enumerate(pdf_image_files): # FYI can't unpack err happens on pages, so we cast w/ enumerate to add in an index
            page_number = idx + 1
            print('INFO (index_pdf.py): page {page_number}'.format(page_number=page_number), pdf_image_file)
            # --- ocr (confused as shit converting PIL.PngImagePlugin.PngImageFile to bytes)
            img_byte_arr = io.BytesIO()
            pdf_image_file.save(img_byte_arr, format='png')
            ocr_str_array = reader.readtext(img_byte_arr.getvalue(), detail=0)
            ocr_text = ' '.join(ocr_str_array) # TODO: might be a way/place to preserve paragraph breaks for encoding
            print('INFO (index_pdf.py): page {page_number} ocr = "{ocr_text}"'.format(page_number=page_number, ocr_text=ocr_text))
            # --- for each chunk, summarize, compile names, create event timeline
            document_text_by_page.append(ocr_text)
        # JOIN ALL TEXT
        document_text = ' '.join(document_text_by_page)
        # SAVE IN CASE ML PARSING FAILS SO WE DONT HAVE TO REDO
        with open(output_filepath, 'w') as outfile:
            json.dump({
                "filename": filename,
                "index_type": "discovery" if is_discovery_document == True else "case_law",
                "document_text": document_text,
                "document_text_by_page": document_text_by_page
            }, outfile, indent=2)

    # GTP3 ML
    print('INFO (index_pdf.py): is_discovery_document = {bool}'.format(bool=is_discovery_document))
    print('INFO (index_pdf.py): len(document_text) = {length}'.format(length=len(document_text)))
    use_repeat_methods = len(document_text) > 11_000 # 4097 tokens allowed, but a token represents 3 or 4 characters
    print('INFO (index_pdf.py): use_repeat_methods = {bool}'.format(bool=use_repeat_methods))

    # --- vectorize document text for summarization
    print('INFO (index_pdf.py): vectors - document_text_vectors')
    chunks_for_vectors = textwrap.wrap(document_text, 3_500)
    for chunk in chunks_for_vectors:
        sleep(2) # slowing down so we don't exceed 60 reqs/min
        safe_chunk = chunk.encode(encoding='ASCII',errors='ignore').decode()
        embedding = gpt_embedding(safe_chunk)
        document_text_vectors.append({ "text": chunk, "vector": embedding })
    # --- per page...
    for idx, page_text in enumerate(document_text_by_page):
        # --- vectorize page text
        print('INFO (index_pdf.py): vectors - document_text_vectors_by_page')
        sleep(2) # slowing down so we don't exceed 60 reqs/min
        safe_page_text = page_text.encode(encoding='ASCII',errors='ignore').decode()
        page_embedding = gpt_embedding(safe_page_text)
        document_text_vectors_by_page.append({ "text": page_text, "vector": page_embedding, "page_number": idx + 1 })
        # --- TODO: vectorize page text paragraphs (not preserved at OCR step, so not sure yet how to do this)
        # --- vectorize page text sentences
        print('INFO (index_pdf.py): vectors - document_text_vectors_by_sentence')
        for page_sentence_text in safe_page_text.split(". "): # doing .\s so we don't split on abbreviations
            sleep(2)
            safe_page_sentence_text = page_sentence_text.encode(encoding='ASCII',errors='ignore').decode()
            page_sentence_embedding = gpt_embedding(safe_page_sentence_text)
            document_text_vectors_by_sentence.append({ "text": page_sentence_text, "vector": page_sentence_embedding, "page_number": idx + 1 })
            

    # --- summary
    print('INFO (index_pdf.py): document_summary')
    if len(document_summary) == 0 and len(document_text) < 250_000:
        document_summary = gpt_summarize(document_text)
    else:
        print('INFO (index_pdf.py): document_summary exists or document is too long')

    # --- classification
    print('INFO (index_pdf.py): document_type')
    if len(document_type) == 0:
        document_type = gpt_completion(
            open_file(get_file_path('./prompts/prompt_document_type.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11_000]),
            max_tokens=75
        )
    else:
        print('INFO (index_pdf.py): document_type exists')

    # --- cases/laws mentioned
    print('INFO (index_pdf.py): mentions_cases_laws')
    if len(document_text) < 250_000:
        if use_repeat_methods == True:
            mentions_cases_laws_dirty = gpt_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')),document_text,text_chunk_size=11_000,return_list=True)
        else:
            mentions_cases_laws_dirty = gpt_completion(open_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')).replace('<<SOURCE_TEXT>>',document_text))
        mentions_cases_laws = filter_empty_strs(gpt_edit(
            open_file(get_file_path('./prompts/edit_clean_list.txt')),
            '\n'.join(mentions_cases_laws_dirty) if use_repeat_methods == True else mentions_cases_laws_dirty # join linebreaks if we have a list
        ).split('\n'))
    else:
        print('INFO (index_pdf.py): mentions_cases_laws skipped because document text is too long')
    
    # --- if a discovery document (ex: police report, testimony, motion)
    if is_discovery_document == True:
        # --- event timeline (split on linebreaks, could later do structured parsing prob of dates)
        print('INFO (index_pdf.py): event_timeline')
        if use_repeat_methods == True:
            event_timeline_dirty = gpt_completion_repeated(open_file(get_file_path('./prompts/prompt_timeline.txt')),document_text,text_chunk_size=11_000,return_list=True)
        else:
            event_timeline_dirty = gpt_completion(open_file(get_file_path('./prompts/prompt_timeline.txt')).replace('<<SOURCE_TEXT>>',document_text))
        event_timeline = filter_empty_strs(gpt_edit(
            open_file(get_file_path('./prompts/edit_event_timeline.txt')),
            '\n'.join(event_timeline_dirty) if use_repeat_methods == True else event_timeline_dirty # join linebreaks if we have a list
        ).split('\n'))
        
        # --- organizations mentioned
        print('INFO (index_pdf.py): mentions_organizations')
        if use_repeat_methods == True:
            mentions_organizations_dirty = gpt_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_organizations.txt')),document_text,text_chunk_size=11_000,return_list=True)
        else:
            mentions_organizations_dirty = gpt_completion(open_file(get_file_path('./prompts/prompt_mentions_organizations.txt')).replace('<<SOURCE_TEXT>>',document_text))
        mentions_organizations = filter_empty_strs(gpt_edit(
            open_file(get_file_path('./prompts/edit_clean_list.txt')),
            '\n'.join(mentions_organizations_dirty) if use_repeat_methods == True else mentions_organizations_dirty # join linebreaks if we have a list
        ).split('\n'))
        
        # --- people mentioned + context within document
        print('INFO (index_pdf.py): mentions_people')
        if use_repeat_methods == True:
            mentions_people_dirty = gpt_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_people.txt')),document_text,text_chunk_size=11_000,return_list=True)
        else:
            mentions_people_dirty = gpt_completion(open_file(get_file_path('./prompts/prompt_mentions_people.txt')).replace('<<SOURCE_TEXT>>',document_text))
        mentions_people = filter_empty_strs(gpt_edit(
            open_file(get_file_path('./prompts/edit_clean_names_list.txt')),
            '\n'.join(mentions_people_dirty) if use_repeat_methods == True else mentions_people_dirty # join linebreaks if we have a list
        ).split('\n'))
        # TODO: skipping follow ups on people bc it takes forever atm. faster dev cycle plz
        # print('INFO (index_pdf.py): mentions_people #{num_people}'.format(num_people=len(mentions_people)))
        # for name in mentions_people:
        #     # TODO: need to build a profile by sifting through the full doc, not just initial big chunk
        #     people[name] = gpt_completion(open_file(get_file_path('./prompts/prompt_mention_involvement.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11_000]).replace('<<NAME>>',name), max_tokens=400)

    # FINISH
    # --- save file
    with open(output_filepath, 'w') as outfile:
        json.dump({
            "document_summary": document_summary,
            "document_text": document_text,
            "document_text_vectors": document_text_vectors,
            "document_text_by_page": document_text_by_page,
            "document_text_vectors_by_page": document_text_vectors_by_page,
            "document_text_vectors_by_paragraph": document_text_vectors_by_paragraph,
            "document_text_vectors_by_sentence": document_text_vectors_by_sentence,
            "document_type": document_type,
            "event_timeline": event_timeline,
            "filename": filename,
            "format": "pdf",
            "index_type": "discovery" if is_discovery_document == True else "case_law",
            "mentions_cases_laws": mentions_cases_laws,
            "mentions_organizations": mentions_organizations,
            "mentions_people": mentions_people,
            "people": people
        }, outfile, indent=2)
    print('INFO (index_pdf.py): saved file')

# RUN
if __name__ == '__main__':
    # affidavit-search-seize.pdf
    # motion-to-unseal.pdf
    filename = input("Filename To Process: ")
    is_discovery_document = input("Discovery document? [y/n]") == 'y'
    index_pdf(filename, "discovery" if is_discovery_document == True else "case_law")