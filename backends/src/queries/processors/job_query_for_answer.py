from models.gpt import gpt_completion
from models.gpt_prompts import gpt_prompt_answer_question

def job_query_for_answer(passage_text, query_text):
    prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', passage_text).replace('<<QUESTION>>', query_text)
    answer = gpt_completion(prompt,max_tokens=150)
    return answer
