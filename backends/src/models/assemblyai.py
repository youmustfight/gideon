import math
import pydash as _
import requests
from time import sleep
import env
from indexers.utils.tokenize_string import TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH

def assemblyai_transcribe(file_upload_url):
    # REQUEST
    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers={ "authorization": env.env_get_assembly_ai_api_key(), "content-type": "application/json" },
        json={ "audio_url": file_upload_url }
    )
    print("INFO (assemblyai_transcript): transcript requested", transcript_response.json())
    transcript_id = transcript_response.json()['id']
    is_transcript_complete = False
    transcript_response = None

    # POLL FOR RESULTS
    while is_transcript_complete == False:
        transcript_check_response = requests.get(
            "https://api.assemblyai.com/v2/transcript/{transcript_id}".format(transcript_id=transcript_id),
            headers={ "authorization": env.env_get_assembly_ai_api_key() },
        )
        print("INFO (assemblyai_transcript.py): transcript check", transcript_check_response.json()['id'], transcript_check_response.json()['status'])
        if transcript_check_response.json()['status'] == 'completed':
            is_transcript_complete = True
            transcript_response = transcript_check_response.json()
        if transcript_check_response.json()['status'] == 'error':
            raise transcript_check_response.json()
        sleep(3)
        
    # PROCESS
    print("INFO (assemblyai_transcript.py): processing response", transcript_response)
    # --- sentences derived from words
    sentences = []
    sentence_milliseconds_start = None
    sentence_milliseconds_end = None
    sentence_text_fragments = []
    for word in transcript_response['words']:
        if (sentence_milliseconds_start == None): sentence_milliseconds_start = word['start']
        sentence_milliseconds_end = word['end']
        sentence_text_fragments.append(word['text'])
        # print("INFO (index_audio.py): word", word)
        # --- if contains a period and word length is significant
        if (_.has_substr(word['text'], ".") and len(word['text']) > 3 and len(" ".join(sentence_text_fragments)) > TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH):
            sentence = {
                "text": " ".join(sentence_text_fragments),
                "second_start": math.floor(sentence_milliseconds_start / 1000),
                "second_end": math.floor(sentence_milliseconds_end / 1000),
            }
            print("INFO (index_audio.py): sentence", sentence)
            sentences.append(sentence)
            sentence_text_fragments = []
            sentence_milliseconds_start = None
            sentence_milliseconds_end = None

    # RETURN
    results = {
        'sentences': sentences,
        'text': transcript_response['text'],
        'words': transcript_response['words'],
    }
    print("INFO (assemblyai_transcript.py): results", results)
    return results
