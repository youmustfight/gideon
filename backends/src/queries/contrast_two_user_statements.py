from models.gpt import gpt_completion, gpt_vars
from models.gpt_prompts import gpt_prompt_contrast_two_statements

def contrast_two_user_statements(user_one, statement_one, user_two, statement_two, engine=gpt_vars()['ENGINE_COMPLETION']):
    print('INFO (GPT3): contrast_two_user_statements - {engine}'.format(engine=engine))
    # --- setup prompt
    prompt = gpt_prompt_contrast_two_statements.replace('<<USER_ONE>>', user_one).replace('<<USER_TWO>>', user_two).replace('<<STATEMENT_ONE>>', statement_one).replace('<<STATEMENT_TWO>>', statement_two)
    # --- summarize
    print('INFO (contrast_two_user_statements.py): prompt\n\n', prompt)
    contrast = gpt_completion(prompt,max_tokens=500,engine=engine)
    return contrast
