from gideon_utils import filter_empty_strs, get_file_path, open_txt_file
import json
import math
import openai
import requests
import textwrap
from time import time,sleep

# SETUP
# --- engines
# https://beta.openai.com/docs/models/gpt-3
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
ENGINE_COMPLETION = 'text-davinci-002' # 'text-ada-001' # 
ENGINE_EDIT = 'text-davinci-edit-001' # free atm because its in beta
ENGINE_EMBEDDING = 'text-similarity-davinci-001'  # 'text-similarity-ada-001' # 'text-similarity-babbage-001' 
TEMPERATURE_DEFAULT = 0

def gpt_vars():
    return {
        "ENGINE_COMPLETION": ENGINE_COMPLETION,
        "ENGINE_EDIT": ENGINE_EDIT,
        "ENGINE_EMBEDDING": ENGINE_EMBEDDING,
        "TEMPERATURE_DEFAULT": TEMPERATURE_DEFAULT
    }

# FUNCTIONS
def gpt_completion(prompt, engine=ENGINE_COMPLETION, temperature=TEMPERATURE_DEFAULT, top_p=1.0, max_tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 2
    retry = 0
    while True:
        try:
            print('INFO (GPT3): gpt_completion - {engine}'.format(engine=engine))
            # --- OpenAI
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            return text
            # --- ForeFront
            # res = requests.post(
            #     "https://shared-api.forefront.link/organization/FV6AbZNxxBmB/gpt-j-6b-vanilla/completions/2JrDQ5BhJAm6",
            #     json={
            #         "text": prompt,
            #         "top_p": top_p,
            #         "top_k": 40,
            #         "temperature": temperature,
            #         "repetition_penalty": 1,
            #         "length": 24
            #     },
            #     headers={
            #         "Authorization": "Bearer {FOREFRONT_API_KEY}".format(FOREFRONT_API_KEY=env['FOREFRONT_API_KEY']),
            #         "Content-Type": "application/json"
            #     }
            # )
            # data = res.json()
            # text = data['result'][0]['completion'].strip()
            # return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Completion): %s" % err
            print('Error (GPT3):', err)
            sleep(1)

def gpt_completion_repeated(prompt_file, text_to_repeatedly_complete, text_chunk_size=6000, return_list=False, dedupe=False):
    print('INFO (GPT3): gpt_completion_repeated')
    chunks = textwrap.wrap(text_to_repeatedly_complete, text_chunk_size)
    result = list();
    for idx, chunk in enumerate(chunks):
        prompt = prompt_file.replace('<<SOURCE_TEXT>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt_completion(prompt, max_tokens=4000-math.floor(text_chunk_size / 3)) # 1 token = 3~4 characters
        print('\n', idx + 1, 'of', len(chunks), ' - ', summary, '\n')
        for split in summary.split("\n"):
            result.append(split)
    # --- TODO: allow dedupe edit at end
    # if dedupe == True:
    # --- return as list or string 
    if return_list == True:
        return filter_empty_strs(result)
    return '\n\n'.join(result)


def gpt_edit(instruction, input, engine=ENGINE_EDIT, temperature=TEMPERATURE_DEFAULT, top_p=1.0):
    max_retry = 2
    retry = 0
    while True:
        try:
            print('INFO (GPT3): gpt_edit')
            # --- OpenAI
            response = openai.Edit.create(
                engine=engine,
                input=input,
                instruction=instruction,
                temperature=temperature,
                top_p=top_p)
            text = response['choices'][0]['text'].strip()
            return text
            # --- ForeFront (doesn't have an edit API endpoint)
            # return input
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Edit): %s" % err
            print('Error (GPT3):', err, instruction, input)
            sleep(1)

def gpt_embedding(content, engine=ENGINE_EMBEDDING):
    print('INFO (GPT3): gpt_embedding - {engine}'.format(engine=engine))
    # --- OpenAI
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector

def gpt_summarize(text_to_recursively_summarize, engine=ENGINE_COMPLETION):
    print('INFO (GPT3): gpt_summarize - {engine}'.format(engine=engine))
    chunks = textwrap.wrap(text_to_recursively_summarize, 11000)
    result = list();
    for idx, chunk in enumerate(chunks):
        prompt = open_txt_file(get_file_path('./prompts/prompt_summary_detailed.txt')).replace('<<SOURCE_TEXT>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt_completion(prompt,max_tokens=500,engine=engine) # limiting inserted completion length to get us to < 2k
        print('\n', idx + 1, 'of', len(chunks), ' - ', summary, '\n')
        result.append(summary)
    results_string = ' '.join(result)
    # --- check if to summarize again 
    if len(results_string) > 4000:
        return gpt_summarize(results_string,engine=engine)
    return results_string
