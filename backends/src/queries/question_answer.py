from gideon_ml import gpt_completion, gpt_embedding, gpt_summarize
from gideon_search import search_similar_file_text_vectors
from gideon_utils import get_file_path, open_file, similarity
import json
import os
import openai

# SETUP
env = json.load(open(get_file_path('../../.env.json')))
# --- OpenAI
openai.api_key = env['OPEN_AI_API_KEY']


# ANSWER A QUESTION
def question_answer(query, index_type):
    print('INFO (question_answer.py): querying "{index_type}" with question "{query}"'.format(index_type=index_type,query=query))
    # VECTOR SIMILARITY SCORING
    search_text_vectors = search_similar_file_text_vectors(query, index_type)
    # SUMMARIZE ANSWER
    print('INFO (question_answer.py): answering from {count} vector(s)...'.format(count=len(search_text_vectors)))
    if len(search_text_vectors) > 0:
        answers = []
        # --- get answer from high similarity vectors
        for idx, tv in enumerate(search_text_vectors):
            prompt = open_file(get_file_path('./prompts/prompt_answer_question.txt')).replace('<<PASSAGE>>', tv['text']).replace('<<QUESTION>>', query)
            answer = gpt_completion(prompt,engine='text-davinci-002',max_tokens=150)
            print('INFO (question_answer.py): answer #{num} = {answer}'.format(answer=answer,num=idx+1))
            answers.append(answer)
        # --- summarize answers
        final_answer = gpt_summarize('\n\n'.join(answers), engine='text-davinci-002')
    else:
        final_answer = 'Found nothing relevant to your question.'
    # ANSWER RESPONSE
    print('INFO (question_answer.py): final_answer = {final_answer}'.format(final_answer=final_answer))
    return final_answer

# RUN
if __name__ == '__main__':
    query = input("Enter your question here: ")
    is_discovery_document_search = input("Searching case law? [y/n]") != 'y'
    question_answer(query, "discovery" if is_discovery_document_search == True else "case_law")
