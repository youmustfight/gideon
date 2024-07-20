import numpy
import requests
import textwrap
from time import sleep
import env
from indexers.utils.tokenize_string import safe_string
from models.gpt_prompts import gpt_prompt_summary_detailed

# SETUP
# we should stop differentiating between model/engine. it's not interchangable. cpt-text/text-davinci-003
# --- engines
# https://beta.openai.com/docs/models/gpt-3
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
# https://openai.com/blog/introducing-text-and-code-embeddings/
# https://beta.openai.com/docs/guides/embeddings/what-are-embeddings
GTP_COMPLETION_MODEL = 'gpt-3.5-turbo' # 'gpt-4-turbo'
# GTP3_COMPLETION_MODEL_ENGINE_DAVINCI_003 = 'text-davinci-003'
GTP3_COMPLETION_MODEL_ENGINE_DAVINCI_002 = 'text-davinci-002' # this seems to handle classification better
# GTP3_EDIT_MODEL_ENGINE = 'text-davinci-edit-001' # free atm because its in beta
GTP3_TEMPERATURE_DEFAULT = 0
OPENAI_REQUEST_TIMEOUT = 60
OPENAI_THROTTLE = 0.2 # 60/req a min. So trying to have a little buffer to miss that limiter

# EMBEDDING
def gpt_embedding(content, engine):
    print(f"INFO (GPT3): gpt_embedding [{engine}] start = {content[0:100]}...")
    try:
        # V2 -- Requests (using this instead of openai package bc it freezes in docker containers for some reason)
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            headers={ 'Authorization': f'Bearer {env.env_get_open_ai_api_key()}', "content-type": "application/json" },
            json={ 'model': engine, 'input': content }
        )
        response = response.json()
        if response.get('error') != None:
            print(response)
            raise response['error']
        # v1 --- setup using faiss (was single embedding)
        # v2 --- setup with easy to use np arrays in a list, handling batch embeddings
        return list(map(lambda d: numpy.asarray(d['embedding'], dtype='float32'), response['data']))
    except Exception as err:
        print(f"ERROR (GPT3): gpt_embedding [{engine}] err = ", err, '\n', content)
        raise err

# COMPLETION
def gpt_completion(prompt, engine=GTP_COMPLETION_MODEL, temperature=0.7, top_p=1.0, max_tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 3
    retry = 0
    while True:
        try:
            print(f'INFO (GPT3): gpt_completion - {engine}: COMPLETE THE "{prompt[0:120]}"...'.replace('\n', ' '))
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={ 'Authorization': f'Bearer {env.env_get_open_ai_api_key()}', "content-type": "application/json" },
                json={
                    'model': engine,
                    'messages': [
                        {'role': 'system', 'content': 'You are a helpful assistant.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'top_p': top_p,
                    'frequency_penalty': freq_pen,
                    'presence_penalty': pres_pen,
                    'stop': stop
                },
            )
            response = response.json()
            if response.get('error') is not None:
                print(response)
                raise Exception(response['error']['message'])
            print('INFO (GPT3): gpt_completion usage: ', response['usage'])
            text = response['choices'][0]['message']['content'].strip()
            print(f'INFO (GPT3): gpt_completion - {engine}: RESPONSE for "{prompt[0:320]}"...'.replace('\n', ' '), text)
            sleep(OPENAI_THROTTLE)
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return f"Error (GTP3 Completion): {err}"
            print('Error (GPT3):', err, '\n', f'{prompt[0:320]}...')

def gpt_edit(prompt, input, engine=GTP_COMPLETION_MODEL, temperature=0.7, top_p=1.0):
    max_retry = 3
    retry = 0
    while True:
        try:
            print(f'INFO (GPT3): gpt_edit: {input[0:80]}...')
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
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return f"Error (GTP3 Edit): {err}"
            print('Error (GPT3):', err, prompt, input)

def gpt_summarize(text_to_recursively_summarize, engine=GTP_COMPLETION_MODEL, max_length=4000, use_prompt=None):
    print('INFO (GPT3): gpt_summarize - {engine}'.format(engine=engine))
    prompt = use_prompt or gpt_prompt_summary_detailed
    chunks = textwrap.wrap(text_to_recursively_summarize, 11000)
    result = list()
    for idx, chunk in enumerate(chunks):
        # use_prompt should be text files
        prompt = safe_string(prompt.replace('<<SOURCE_TEXT>>', chunk))
        # TEST: not sure if we should limit token length
        # max_tokens_from_length = math.floor(max_length / 3) # read online that a token is 3~4 characters
        # max_tokens = min(max_tokens_from_length, 500)
        summary = gpt_completion(prompt, max_tokens=500, engine=engine) # limiting inserted completion length to get us to < 2k
        print('\n', idx + 1, 'of', len(chunks), ' - ', summary, '\n')
        result.append(summary)
    results_string = ' '.join(result)
    # --- check if to summarize again (this can get stuck in a loop if it can't summarize further)
    if len(results_string) > max_length:
        return gpt_summarize(results_string, engine=engine, use_prompt=use_prompt)
    return results_string
