

from models.gpt import gpt_completion, gpt_vars
from files.file_utils import get_file_path, open_txt_file


def contrast_two_user_statements(user_one, statement_one, user_two, statement_two, engine=gpt_vars()['ENGINE_COMPLETION']):
    print('INFO (GPT3): contrast_two_user_statements - {engine}'.format(engine=engine))
    # --- setup prompt
    prompt = open_txt_file(get_file_path('./prompts/prompt_contrast_two_statements.txt')).replace('<<USER_ONE>>', user_one).replace('<<USER_TWO>>', user_two).replace('<<STATEMENT_ONE>>', statement_one).replace('<<STATEMENT_TWO>>', statement_two)
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    # --- summarize
    print('INFO (contrast_two_user_statements.py): prompt\n\n', prompt)
    contrast = gpt_completion(prompt,max_tokens=500,engine=engine)
    return contrast
