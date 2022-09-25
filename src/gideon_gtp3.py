from gideon_utils import filter_empty_strs, get_file_path, open_file
import math
import openai
import re
import textwrap
from time import time,sleep

def gpt3_completion(prompt, engine='text-davinci-002', temp=0.5, top_p=1.0, max_tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 2
    retry = 0
    while True:
        try:
            print('Info (OpenAI): gpt3_completion')
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            # print(response['choices'])
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Completion): %s" % err
            print('Error (OpenAI):', err)
            sleep(1)

def gpt3_completion_repeated(prompt_file, text_to_repeatedly_complete, text_chunk_size=6000, return_list=False, dedupe=False):
    print('Info (OpenAI): gpt3_completion_repeated')
    chunks = textwrap.wrap(text_to_repeatedly_complete, text_chunk_size)
    result = list();
    for index, chunk in enumerate(chunks):
        prompt = prompt_file.replace('<<SOURCE_TEXT>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt, max_tokens=4000-math.floor(text_chunk_size / 3)) # 1 token = 3~4 characters
        print('\n\n', index + 1, 'of', len(chunks), ' - ', summary)
        for split in summary.split("\n"):
            result.append(split)
    # --- TODO: allow dedupe edit at end
    # if dedupe == True:
    # --- return as list or string 
    if return_list == True:
        return filter_empty_strs(result)
    return '\n\n'.join(result)


def gpt3_edit(instruction, input, engine='text-davinci-edit-001', temp=0, top_p=1.0):
    max_retry = 2
    retry = 0
    while True:
        try:
            print('Info (OpenAI): gpt3_edit')
            response = openai.Edit.create(
                engine=engine,
                input=input,
                instruction=instruction,
                temperature=temp,
                top_p=top_p)
            # print(response['choices'])
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as err:
            retry += 1
            if retry >= max_retry:
                return "Error (GTP3 Edit): %s" % err
            print('Error (OpenAI):', err, instruction, input)
            sleep(1)

def gpt3_summarize(text_to_recursively_summarize):
    print('Info (OpenAI): gpt3_summarize')
    chunks = textwrap.wrap(text_to_recursively_summarize, 11000)
    result = list();
    for index, chunk in enumerate(chunks):
        prompt = open_file(get_file_path('./prompts/prompt_summary_detailed.txt')).replace('<<SOURCE_TEXT>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt, max_tokens=750) # limiting inserted completion length to get us to < 2k
        print('\n\n', index + 1, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    results_string = ' '.join(result)
    # --- check if to summarize again 
    if len(results_string) > 4000:
        return gpt3_summarize(results_string)
    return results_string
