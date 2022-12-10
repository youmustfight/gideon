from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_pdf import index_pdf
from indexers.utils.index_document_content_vectors import index_document_content_vectors
from models.gpt import gpt_completion, gpt_summarize
from models.gpt_prompts import gpt_prompt_answer_question

def job_query_for_answer(passage_text, query_text):
    prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', passage_text).replace('<<QUESTION>>', query_text)
    answer = gpt_completion(prompt,max_tokens=150)
    return answer
