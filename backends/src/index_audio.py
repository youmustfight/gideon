from gideon_ml import gpt_completion, gpt_embedding, gpt_summarize
from gideon_utils import get_file_path, open_file
import json
import math
import requests
import textwrap
from time import sleep

# SETUP
env = json.load(open(get_file_path('../../.env.json')))

# provided by https://www.assemblyai.com/docs/walkthroughs#uploading-local-files-for-transcription
def read_file(path_to_file, chunk_size=5242880):
    with open(path_to_file, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

# INDEX AUDIO
def index_audio(filename):
    print("INFO (index_audio.py): started")
    input_filepath = get_file_path('../documents/{filename}'.format(filename=filename))
    output_filepath = get_file_path('../indexed/{filename}.json'.format(filename=filename))
    # --- Upload to AssemblyAI
    # provided by https://www.assemblyai.com/docs/walkthroughs#uploading-local-files-for-transcription
    upload_response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers={ "authorization": env['ASSEMBLY_AI_API_KEY'] },
        data=read_file(input_filepath)
    )
    upload_url = upload_response.json()['upload_url']
    print("INFO (index_audio.py): file uploaded", upload_url)
    # --- Start transcript processing with returned upload_url
    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers={ "authorization": env['ASSEMBLY_AI_API_KEY'], "content-type": "application/json" },
        json={ "audio_url": upload_url }
    )
    print("INFO (index_audio.py): transcript requested", transcript_response.json())
    transcript_id = transcript_response.json()['id']
    is_transcript_complete = False
    transcript_completed = None
    while is_transcript_complete == False:
        transcript_check_response = requests.get(
            "https://api.assemblyai.com/v2/transcript/{transcript_id}".format(transcript_id=transcript_id),
            headers={ "authorization": env['ASSEMBLY_AI_API_KEY'] },
        )
        print("INFO (index_audio.py): transcript check", transcript_check_response.json()['id'], transcript_check_response.json()['status'])
        if transcript_check_response.json()['status'] == 'completed':
            is_transcript_complete = True
            transcript_completed = transcript_check_response.json()
        sleep(3)

    # Setup Vars
    document_text = ''
    document_text_vectors = [] # { text, vector }[]
    document_text_by_minute = []  # string[]
    document_text_vectors_by_minute = [] # { text, vector, page_number }[]
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

    # GPT3
    # --- save audio text
    document_text = transcript_completed['text']
    # --- vectorize audio text: document
    print('INFO (index_audio.py): vectors - document_text_vectors')
    chunks_for_vectors = textwrap.wrap(document_text, 3_500)
    for chunk in chunks_for_vectors:
        sleep(2) # slowing down so we don't exceed 60 reqs/min
        safe_chunk = chunk.encode(encoding='ASCII',errors='ignore').decode()
        embedding = gpt_embedding(safe_chunk)
        document_text_vectors.append({ "text": chunk, "vector": embedding })
    # --- vectorize audio text: by minute
    milliseconds_start = 0
    milliseconds_end = 1000 * 60 # 1 min interval
    has_more_transcription_to_embed = True
    transcript_words = transcript_completed['words']
    while has_more_transcription_to_embed == True:
        def is_text_within_interval(assemblyai_text):
            return assemblyai_text['start'] > milliseconds_start and assemblyai_text['start'] < milliseconds_end
        def map_text_within_interval(assemblyai_text):
            return assemblyai_text['text']
        text_snippets_within_minute = map(map_text_within_interval, list(filter(is_text_within_interval, transcript_words)))
        text_within_minute = ' '.join(text_snippets_within_minute)
        print('INFO (index_audio.py): vectors - text_within_minute', text_within_minute)
        if len(text_within_minute) > 0:
            safe_minute_text = text_within_minute.encode(encoding='ASCII',errors='ignore').decode()
            minute_embedding = gpt_embedding(safe_minute_text)
            document_text_by_minute.append(text_within_minute)
            document_text_vectors_by_minute.append({ "text": text_within_minute, "vector": minute_embedding, "minute_number": math.ceil((milliseconds_end / 1000) / 60) })
            # --- increment start/end by a minute
            milliseconds_start = milliseconds_start + (1000 * 60)
            milliseconds_end = milliseconds_end + (1000 * 60)
        else:
            has_more_transcription_to_embed = False
    # --- vectorize audio text: by sentence
    print('INFO (index_pdf.py): vectors - document_text_vectors_by_sentence')
    for page_sentence_text in document_text.split(". "): # TODO OPTIMIZE: doing .\s so we don't split on abbreviations
        sleep(2)
        safe_page_sentence_text = page_sentence_text.encode(encoding='ASCII',errors='ignore').decode()
        page_sentence_embedding = gpt_embedding(safe_page_sentence_text)
        document_text_vectors_by_sentence.append({ "text": page_sentence_text, "vector": page_sentence_embedding, "minute_number": 0 }) # TODO
    
    # --- summary
    print('INFO (index_audio.py): document_summary')
    if len(document_text) < 250_000:
        document_summary = gpt_summarize(document_text)
    else:
        print('INFO (index_audio.py): document is too long')
    # --- classification
    print('INFO (index_audio.py): document_type')
    if len(document_type) == 0:
        document_type = gpt_completion(
            open_file(get_file_path('./prompts/prompt_document_type.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11_000]),
            max_tokens=75
        )
    else:
        print('INFO (index_audio.py): document_type exists')

    # FINISH
    # --- save file
    with open(output_filepath, 'w') as outfile:
        json.dump({
            "document_summary": document_summary,
            "document_text": document_text,
            "document_text_by_minute": document_text_by_minute,
            "document_text_vectors": document_text_vectors,
            "document_text_vectors_by_minute": document_text_vectors_by_minute,
            "document_text_vectors_by_paragraph": document_text_vectors_by_paragraph,
            "document_text_vectors_by_sentence": document_text_vectors_by_sentence,
            "document_type": document_type,
            "event_timeline": event_timeline,
            "filename": filename,
            "format": "audio",
            "index_type": "discovery",
            "mentions_cases_laws": mentions_cases_laws,
            "mentions_organizations": mentions_organizations,
            "mentions_people": mentions_people,
            "people": people
        }, outfile, indent=2)
    print('INFO (index_audio.py): saved file')

# RUN
if __name__ == '__main__':
    # affidavit-search-seize.pdf
    filename = input("Filename To Process: ")
    index_audio(filename)
