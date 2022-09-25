import easyocr
import io
import json
from gideon_utils import filter_empty_strs, get_file_path, open_file
from gideon_gtp3 import gpt3_completion, gpt3_completion_repeated, gpt3_edit, gpt3_embedding, gpt3_summarize
import openai
import os
from pdf2image import convert_from_path # FYI, on Mac -> brew install poppler
import textwrap

# SETUP
env = json.load(open(get_file_path('../.env.json')))
# --- OpenAI
openai.api_key = env['OPEN_AI_API_KEY']
# --- OCR
reader = easyocr.Reader(['en'])


# RUN
if __name__ == '__main__':
    print('INFO (intake_file.py): started')

    # FILE + PROPERTIES (w/ OCR)
    # affidavit-search-seize.pdf
    # motion-to-unseal.pdf
    filename = input("Filename To Process: "); 
    is_discovery_document = input("Discovery document? [y/n]") == 'y'
    input_filepath = get_file_path('../files/{filename}'.format(filename=filename))
    output_filepath = get_file_path('../outputs/{filename}.json'.format(filename=filename))
    # --- docs: all
    document_text = ''
    pages_as_text = []
    document_type = ''
    document_summary = ''
    text_vectors = []
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
        document_summary = existing_data['document_summary']
        pages_as_text = existing_data['pages_as_text']
        # text_vectors = existing_data['text_vectors']
    else:
        # CONVERT (PDF -> Image[] for OCR)
        print('INFO (intake_file.py): converting {convert_file_path}'.format(convert_file_path=input_filepath))
        pdf_image_files = convert_from_path(input_filepath, fmt='png')
        print('INFO (intake_file.py): converted {convert_file_path}'.format(convert_file_path=input_filepath))
        # PER PAGE (get text)
        for idx, pdf_image_file in enumerate(pdf_image_files): # FYI can't unpack err happens on pages, so we cast w/ enumerate to add in an index
            page_number = idx + 1
            print('INFO (intake_file.py): page {page_number}'.format(page_number=page_number), pdf_image_file)
            # --- ocr (confused as shit converting PIL.PngImagePlugin.PngImageFile to bytes)
            img_byte_arr = io.BytesIO()
            pdf_image_file.save(img_byte_arr, format='png')
            ocr_str_array = reader.readtext(img_byte_arr.getvalue(), detail=0)
            ocr_text = ' '.join(ocr_str_array)
            print('INFO (intake_file.py): page {page_number} ocr = "{ocr_text}"'.format(page_number=page_number, ocr_text=ocr_text))
            # --- for each chunk, summarize, compile names, create event timeline
            pages_as_text.append(ocr_text)
        # JOIN ALL TEXT
        document_text = ' '.join(pages_as_text)
        # SAVE IN CASE ML PARSING FAILS SO WE DONT HAVE TO REDO
        with open(output_filepath, 'w') as outfile:
            json.dump({
                "document_text": document_text,
                "pages_as_text": pages_as_text
            }, outfile, indent=2)

    # GTP3 ML
    print('INFO (intake_file.py): is_discovery_document = {bool}'.format(bool=is_discovery_document))
    print('INFO (intake_file.py): len(document_text) = {length}'.format(length=len(document_text)))
    use_repeat_methods = len(document_text) > 11000 # 4097 tokens allowed, but a token represents 3 or 4 characters
    print('INFO (intake_file.py): use_repeat_methods = {bool}'.format(bool=use_repeat_methods))

    # --- vectorize content for similarity scoring later to help with search
    print('INFO (intake_file.py): vectors')
    chunks_for_vectors = textwrap.wrap(document_text, 3500)
    for chunk in chunks_for_vectors:
        safe_chunk = chunk.encode(encoding='ASCII',errors='ignore').decode()
        embedding = gpt3_embedding(safe_chunk)
        text_vectors.append({ "text": chunk, "vector": embedding })

    # --- summary
    print('INFO (intake_file.py): document_summary')
    if len(document_summary) == 0:
        document_summary = gpt3_summarize(document_text)

    # --- classification
    print('INFO (intake_file.py): document_type')
    document_type = gpt3_completion(
        open_file(get_file_path('./prompts/prompt_document_type.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11000]),
        max_tokens=75
    )

    # --- cases/laws mentioned
    print('INFO (intake_file.py): mentions_cases_laws')
    if use_repeat_methods == True:
        mentions_cases_laws_dirty = gpt3_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')),document_text,text_chunk_size=11000,return_list=True)
    else:
        mentions_cases_laws_dirty = gpt3_completion(open_file(get_file_path('./prompts/prompt_mentions_cases_laws.txt')).replace('<<SOURCE_TEXT>>',document_text))
    mentions_cases_laws = filter_empty_strs(gpt3_edit(
        open_file(get_file_path('./prompts/edit_clean_list.txt')),
        '\n'.join(mentions_cases_laws_dirty) if use_repeat_methods == True else mentions_cases_laws_dirty # join linebreaks if we have a list
    ).split('\n'))
    
    # --- if a discovery document (ex: police report, testimony, motion)
    if is_discovery_document == True:
        # --- event timeline (split on linebreaks, could later do structured parsing prob of dates)
        print('INFO (intake_file.py): event_timeline')
        if use_repeat_methods == True:
            event_timeline_dirty = gpt3_completion_repeated(open_file(get_file_path('./prompts/prompt_timeline.txt')),document_text,text_chunk_size=11000,return_list=True)
        else:
            event_timeline_dirty = gpt3_completion(open_file(get_file_path('./prompts/prompt_timeline.txt')).replace('<<SOURCE_TEXT>>',document_text))
        event_timeline = filter_empty_strs(gpt3_edit(
            open_file(get_file_path('./prompts/edit_event_timeline.txt')),
            '\n'.join(event_timeline_dirty) if use_repeat_methods == True else event_timeline_dirty # join linebreaks if we have a list
        ).split('\n'))
        
        # --- organizations mentioned
        print('INFO (intake_file.py): mentions_organizations')
        if use_repeat_methods == True:
            mentions_organizations_dirty = gpt3_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_organizations.txt')),document_text,text_chunk_size=11000,return_list=True)
        else:
            mentions_organizations_dirty = gpt3_completion(open_file(get_file_path('./prompts/prompt_mentions_organizations.txt')).replace('<<SOURCE_TEXT>>',document_text))
        mentions_organizations = filter_empty_strs(gpt3_edit(
            open_file(get_file_path('./prompts/edit_clean_list.txt')),
            '\n'.join(mentions_organizations_dirty) if use_repeat_methods == True else mentions_organizations_dirty # join linebreaks if we have a list
        ).split('\n'))
        
        # --- people mentioned + context within document
        print('INFO (intake_file.py): mentions_people')
        if use_repeat_methods == True:
            mentions_people_dirty = gpt3_completion_repeated(open_file(get_file_path('./prompts/prompt_mentions_people.txt')),document_text,text_chunk_size=11000,return_list=True)
        else:
            mentions_people_dirty = gpt3_completion(open_file(get_file_path('./prompts/prompt_mentions_people.txt')).replace('<<SOURCE_TEXT>>',document_text))
        mentions_people = filter_empty_strs(gpt3_edit(
            open_file(get_file_path('./prompts/edit_clean_names_list.txt')),
            '\n'.join(mentions_people_dirty) if use_repeat_methods == True else mentions_people_dirty # join linebreaks if we have a list
        ).split('\n'))
        print('INFO (intake_file.py): mentions_people #{num_people}'.format(num_people=len(mentions_people)))
        for name in mentions_people:
            # TODO: need to build a profile by sifting through the full doc, not just initial big chunk
            people[name] = gpt3_completion(open_file(get_file_path('./prompts/prompt_mention_involvement.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11000]).replace('<<NAME>>',name), max_tokens=400)


    # FINISH
    # --- save file
    with open(output_filepath, 'w') as outfile:
        json.dump({
            "index_type": "discovery" if is_discovery_document == True else "case_law",
            "document_summary": document_summary,
            "document_text": document_text,
            "document_type": document_type,
            "event_timeline": event_timeline,
            "filename": filename,
            "mentions_cases_laws": mentions_cases_laws,
            "mentions_organizations": mentions_organizations,
            "mentions_people": mentions_people,
            "pages_as_text": pages_as_text,
            "people": people,
            "text_vectors": text_vectors
        }, outfile, indent=2)