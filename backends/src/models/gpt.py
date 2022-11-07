from env import env_get_open_ai_api_key
from gideon_utils import filter_empty_strs, get_file_path, open_txt_file
import numpy
import math
import openai
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
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()

def gpt_vars():
    return {
        "ENGINE_COMPLETION": ENGINE_COMPLETION,
        "ENGINE_EDIT": ENGINE_EDIT,
        "ENGINE_EMBEDDING": ENGINE_EMBEDDING,
        "TEMPERATURE_DEFAULT": TEMPERATURE_DEFAULT
    }

def gpt_embedding(content, engine=ENGINE_EMBEDDING):
    print(f"INFO (GPT3): gpt_embedding [{engine}] start = {content}")
    try:
        response = openai.Embedding.create(input=content,engine=engine,request_timeout=10) # OpenAI
        vector = response['data'][0]['embedding']  # this is a normal list
        # to be work well w/ faiss, we should return embeddings in shape of #, dimensions
        # re: float32 https://github.com/facebookresearch/faiss/issues/461#issuecomment-392259327
        vector_as_numpy_array = numpy.asarray(vector, dtype="float32")
        vector_shaped_for_consistency_with_faiss = numpy.expand_dims(vector_as_numpy_array, axis=0) # matching the matrix style of sentence-transformer clip encode returns, which works with faiss
        print(f"INFO (GPT3): gpt_embedding [{engine}] finish", vector_shaped_for_consistency_with_faiss)
        return vector_shaped_for_consistency_with_faiss
    except Exception as err:
        print(f"ERROR (GPT3): gpt_embedding", err)
        raise err

# FUNCTIONS
def gpt_completion(prompt, engine=ENGINE_COMPLETION, temperature=TEMPERATURE_DEFAULT, top_p=1.0, max_tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 2
    retry = 0
    while True:
        try:
            print(f'INFO (GPT3): gpt_completion - {engine}: {prompt[0:240]}...')
            # --- OpenAI
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop,
                request_timeout=10,
            )
            text = response['choices'][0]['text'].strip()
            print(f'INFO (GPT3): gpt_completion - {engine}: {prompt[0:240]}...', text)
            return text
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
                top_p=top_p,
                request_timeout=10
            )
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Edit): %s" % err
            print('Error (GPT3):', err, instruction, input)
            sleep(1)

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
