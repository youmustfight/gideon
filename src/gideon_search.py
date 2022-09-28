from gideon_ml import gpt_embedding
from gideon_utils import get_documents_json, similarity

def sort_scored_text_vectors(text_vectors):
    return sorted(text_vectors, key=lambda d: d['score'], reverse=True)

def get_top_score_of_text_vectors(text_vectors):
    sorted = sort_scored_text_vectors(text_vectors)
    return sorted[0]['score']

def filter_text_vectors_within_top_score_diff(text_vectors, percentage_diff=0.2):
    sorted = sort_scored_text_vectors(text_vectors)
    top_score = get_top_score_of_text_vectors(text_vectors)
    top_text_vectors = []
    print('INFO (gideon_search.py) filter_text_vectors_within_top_score_diff score: {top_score}'.format(top_score=top_score))
    for tv in sorted:
        diff = (top_score * percentage_diff)
        score = tv['score']
        # print('INFO (gideon_search.py):  {score} > ({top_score} - {diff})'.format(top_score=top_score,diff=diff,score=score))
        if score > (top_score - diff):
            top_text_vectors.append(tv)
    return top_text_vectors

# SEARCH HELPERS
# TODO: comparison against document vectors vs page vectors
def get_all_document_text_vectors(index_type, vector_type='document'):
    print('INFO (gideon_search.py): get_all_document_text_vectors', index_type, vector_type)
    text_vectors = []
    json_documents = get_documents_json()
    print('INFO (gideon_search.py): num json_documents', len(json_documents))
    # --- for each json file
    for json_document_payload in json_documents:
        # --- skip files that don't match type (so we don't confuse discovery docs with case law)
        if json_document_payload['index_type'] != index_type:
            continue
        # --- push each text_vector {}
        if vector_type == 'document':
            for tv in json_document_payload['document_text_vectors']:
                text_vectors.append(tv)
        # TODO: why are page/minute embeds so much worse for both pdf/audio lol 
        # elif vector_type == 'page':
        #     print('INFO (gideon_search.py): json_document_payload', json_document_payload['filename'])
        #     if json_document_payload['format'] == 'pdf':
        #         for tv in json_document_payload['document_text_vectors_by_page']:
        #             text_vectors.append(tv)
        #     # Doing large scale for audio because minute intervals seem to lead to more making up/filling in gaps from prior history
        #     elif json_document_payload['format'] == 'audio':
        #         for tv in json_document_payload['document_text_vectors']:
        #             text_vectors.append(tv)
        else:
            print('ERROR (gideon_search.py): Unexpected vector_type {vector_type}'.format(vector_type=vector_type))
    print('INFO (gideon_search.py): get_all_document_text_vectors - vectors found: #{num}'.format(num=len(text_vectors)))
    return text_vectors

def search_similar_file_text_vectors(text, index_type, count=5):
    print('INFO (gideon_search.py): search_similar_file_text_vectors')
    vector = gpt_embedding(text)
    # print('INFO (gideon_search.py): search_similar_file_text_vectors vector:', vector)
    # --- get vectors
    text_vectors = get_all_document_text_vectors(index_type, 'document') # sticking with document bc page is terrible
    print('INFO (gideon_search.py): text_vectors')
    text_vectors_scored = []
    # --- score vectors
    for tv in text_vectors:
        score = similarity(vector, tv['vector'])
        # --- skip low scores
        if score > 0.2:
            text_vectors_scored.append({ 'score': score , 'text': tv['text'] })
    # --- bad scores/query
    if len(text_vectors_scored) == 0:
        return []
    text_vectors_scored = sort_scored_text_vectors(text_vectors_scored)
    # --- filter for scores within 10% of top score (used to do count, but for small sets of data that can bring in bad answers)
    top_score = get_top_score_of_text_vectors(text_vectors_scored)
    print('INFO (gideon_search.py): search_similar_file_text_vectors top score = {top_score}'.format(top_score=top_score))
    top_text_vectors = filter_text_vectors_within_top_score_diff(text_vectors_scored, 0.1)
    # --- return
    # TEST: seeing if just utilizing all vectors based on scores/relations is better than hard limit
    # return top_text_vectors[0:count]
    return top_text_vectors
