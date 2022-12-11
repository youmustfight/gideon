import env
from models.gpt_prompts import gpt_prompt_summary_detailed
from utils import filter_empty_strs
import numpy
import requests
import textwrap
from time import sleep

# SETUP
# we should stop differentiating between model/engine. it's not interchangable. cpt-text/text-davinci-003
# --- engines
# https://beta.openai.com/docs/models/gpt-3
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
# https://openai.com/blog/introducing-text-and-code-embeddings/
# https://beta.openai.com/docs/guides/embeddings/what-are-embeddings
GTP3_COMPLETION_MODEL_ENGINE = 'text-davinci-003' # 'text-ada-001'
GTP3_EDIT_MODEL_ENGINE = 'text-davinci-edit-001' # free atm because its in beta
GTP3_TEMPERATURE_DEFAULT = 0
OPENAI_REQUEST_TIMEOUT = 60
OPENAI_THROTTLE = 1.2

# EMBEDDING
def gpt_embedding(content, engine):
    print(f"INFO (GPT3): gpt_embedding [{engine}] start = {content}")
    try:
        # V2 -- Requests (using this instead of openai package bc it freezes in docker containers for some reason)
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            headers={ 'Authorization': f'Bearer {env.env_get_open_ai_api_key()}', "content-type": "application/json" },
            json={ 'model': engine, 'input': content }
        )
        response = response.json()
        # v1 --- setup using faiss (was single embedding)
        # v2 --- setup with easy to use np arrays in a list, handling batch embeddings
        return list(map(lambda d: numpy.asarray(d['embedding'], dtype='float32'), response['data']))
    except Exception as err:
        print(f"ERROR (GPT3): gpt_embedding [{engine}] err = ", err, content)
        raise err

# COMPLETION
def gpt_completion(prompt, engine=GTP3_COMPLETION_MODEL_ENGINE, temperature=GTP3_TEMPERATURE_DEFAULT, top_p=1.0, max_tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 3
    retry = 0
    while True:
        try:
            print(f'INFO (GPT3): gpt_completion - {engine}: COMPLETE THE "{prompt[0:120]}"...'.replace('\n', ' '))
            # V2 -- Requests (using this instead of openai package bc it freezes in docker containers for some reason)
            response = requests.post(
                'https://api.openai.com/v1/completions',
                headers={ 'Authorization': f'Bearer {env.env_get_open_ai_api_key()}', "content-type": "application/json" },
                json={
                    'model': engine,
                    'prompt': prompt,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'top_p': top_p,
                    'frequency_penalty': freq_pen,
                    'presence_penalty': pres_pen,
                    'stop': stop
                },
            )
            response = response.json()
            # print(response)
            text = response['choices'][0]['text'].strip()
            print(f'INFO (GPT3): gpt_completion - {engine}: RESPONSE for "{prompt[0:120]}"...'.replace('\n', ' '), text)
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Completion): %s" % err
            print('Error (GPT3):', err)

def gpt_edit(prompt, input, engine=GTP3_EDIT_MODEL_ENGINE, temperature=GTP3_TEMPERATURE_DEFAULT, top_p=1.0):
    max_retry = 3
    retry = 0
    while True:
        try:
            print(f'INFO (GPT3): gpt_edit: {input[0:80]}...')
            # --- OpenAI
            response = requests.post(
                'https://api.openai.com/v1/edits',
                headers={ 'Authorization': f'Bearer {env.env_get_open_ai_api_key()}', "content-type": "application/json" },
                json={
                    'model': engine,
                    'input': input,
                    'instruction': prompt,
                    'temperature': temperature,
                    'top_p': top_p
                },
            )
            response = response.json()
            # print(response)
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Edit): %s" % err
            print('Error (GPT3):', err, prompt, input)

def gpt_summarize(text_to_recursively_summarize, engine=GTP3_COMPLETION_MODEL_ENGINE, max_length=4000, use_prompt=gpt_prompt_summary_detailed):
    print('INFO (GPT3): gpt_summarize - {engine}'.format(engine=engine))
    chunks = textwrap.wrap(text_to_recursively_summarize, 11000)
    result = list()
    for idx, chunk in enumerate(chunks):
        # use_prompt should be text files
        prompt = use_prompt.replace('<<SOURCE_TEXT>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        # TEST: not sure if we should limit token length
        # max_tokens_from_length = math.floor(max_length / 3) # read online that a token is 3~4 characters
        # max_tokens = min(max_tokens_from_length, 500)
        summary = gpt_completion(prompt,max_tokens=500,engine=engine) # limiting inserted completion length to get us to < 2k
        print('\n', idx + 1, 'of', len(chunks), ' - ', summary, '\n')
        result.append(summary)
    results_string = ' '.join(result)
    # --- check if to summarize again (this can get stuck in a loop if it can't summarize further)
    if len(results_string) > max_length:
        return gpt_summarize(results_string,engine=engine)
    return results_string
