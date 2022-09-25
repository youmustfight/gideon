from gideon_gtp3 import gpt3_completion, gpt3_embedding, gpt3_summarize
from gideon_utils import get_file_path, open_file, similarity
import json
import os
import openai

# SETUP
env = json.load(open(get_file_path('../.env.json')))
# --- OpenAI
openai.api_key = env['OPEN_AI_API_KEY']

# SEARCH HELPERS
def get_all_text_vectors(index_type):
    print('INFO (query.py): get_all_text_vectors')
    text_vectors = []
    path_to_json = get_file_path("../outputs")
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    # --- for each json file
    for json_filename in json_files:
        json_file_payload = json.load(open(get_file_path('../outputs/{json_filename}'.format(json_filename=json_filename))))
        # --- skip files that don't match type (so we don't confuse discovery docs with case law)
        if json_file_payload['index_type'] != index_type:
            continue
        # --- push each text_vector {}
        for tv in json_file_payload['text_vectors']:
            text_vectors.append(tv)
    print('INFO (query.py): get_all_text_vectors - vectors found: #{num}'.format(num=len(text_vectors)))
    return text_vectors

def search_similar_file_text_vectors(text, index_type, count=3):
    print('INFO (query.py): search_similar_file_text_vectors')
    vector = gpt3_embedding(text)
    # print('INFO (query.py): search_similar_file_text_vectors vector:', vector)
    text_vectors = get_all_text_vectors(index_type)
    scores = []
    for tv in text_vectors:
        score = similarity(vector, tv['vector'])
        scores.append({ 'score': score , 'text': tv['text'] })
    ordered = sorted(scores, key=lambda d: d['score'], reverse=True)
    return ordered[0:count]

# RUN
if __name__ == '__main__':
    print('INFO (query.py): started')
    # INPUT
    query = input("Enter your question here: ")
    is_discovery_document_search = input("Searching case law? [y/n]") != 'y'
    index_type = type="discovery" if is_discovery_document_search == True else "case_law"
    print('INFO (query.py): querying "{index_type}" with question "{query}"'.format(index_type=index_type,query=query))

    # VECTOR SIMILARITY SCORING
    search_text_vectors = search_similar_file_text_vectors(query, index_type)

    # SUMMARIZE ANSWER
    print('INFO (query.py): answering....')
    answers = []
    # --- get answer from high similarity vectors
    for idx, tv in enumerate(search_text_vectors):
        prompt = open_file(get_file_path('./prompts/prompt_answer_question.txt')).replace('<<PASSAGE>>', tv['text']).replace('<<QUESTION>>', query)
        answer = gpt3_completion(prompt)
        print('INFO (query.py): answer #{num} = {answer}'.format(answer=answer,num=idx+1))
        answers.append(answer)
    # --- summarize answers
    final_answer = gpt3_summarize('\n\n'.join(answers))

    # ANSWER RESPONSE
    print('INFO (query.py): final_answer = {final_answer}'.format(final_answer=final_answer))