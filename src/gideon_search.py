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
def get_all_document_text_vectors(index_type, vector_type='docuemnt'):
    print('INFO (gideon_search.py): get_all_document_text_vectors')
    text_vectors = []
    json_documents = get_documents_json()
    # --- for each json file
    for json_document_payload in json_documents:
        # --- skip files that don't match type (so we don't confuse discovery docs with case law)
        if json_document_payload['index_type'] != index_type:
            continue
        # --- push each text_vector {}
        if vector_type == "page":
            for tv in json_document_payload['document_text_vectors']:
                text_vectors.append(tv)
        else:
            for tv in json_document_payload['document_text_vectors']:
                text_vectors.append(tv)
    print('INFO (gideon_search.py): get_all_document_text_vectors - vectors found: #{num}'.format(num=len(text_vectors)))
    return text_vectors

def search_similar_file_text_vectors(text, index_type, count=5):
    print('INFO (gideon_search.py): search_similar_file_text_vectors')
    vector = gpt_embedding(text)
    # print('INFO (gideon_search.py): search_similar_file_text_vectors vector:', vector)
    # --- get vectors
    text_vectors = get_all_document_text_vectors(index_type, 'page')
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
    top_text_vectors = filter_text_vectors_within_top_score_diff(text_vectors_scored, 0.2)
    # --- return
    return top_text_vectors[0:count]
