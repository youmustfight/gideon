from env import env_get_open_ai_api_key
from gideon_gpt import gpt_completion, gpt_embedding, gpt_summarize
from gideon_search import filter_text_vectors_within_top_score_diff, search_similar_file_text_vectors, sort_scored_text_vectors
from gideon_utils import filter_formats, get_documents_json, get_file_path, open_txt_file, similarity
import openai

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()


# SEARCH QUERY
def search_for_locations_by_text_embedding(text_query_embedding):
    print('INFO (search_for_locations_by_vector.py): query all documents for vector', text_query_embedding)
    # SETUP
    # --- files
    json_documents = get_documents_json()
    json_documents = filter_formats(["audio", "pdf", "video"], json_documents)
    locations = [] # { filename, page_number, score }[]
    # VECTOR SIMILARITY SCORING
    # --- for each file
    for json_document_payload in json_documents:
        # --- for each document_text_vectors_by_sentence (did _by_page but i think this will be higher accuracy)
        for sentence_text_vector in json_document_payload['document_text_vectors_by_sentence']:
            # TODO: at document vector creation, we should stitch short phrases together. small phrases are getting high similarity scores
            if len(sentence_text_vector['text']) > 50:
                # --- check min similarity
                document_score = similarity(text_query_embedding, sentence_text_vector['vector'])
                # --- push to locations w/ 
                location_to_push = {
                    "format": json_document_payload['format'],
                    "filename": json_document_payload["filename"],
                    "score": document_score,
                    "text": sentence_text_vector['text']
                }
                if json_document_payload['format'] == 'pdf':
                    location_to_push['page_number'] = sentence_text_vector['page_number']
                elif json_document_payload['format'] == 'audio':
                    location_to_push['minute_number'] = sentence_text_vector['minute_number']
                locations.append(location_to_push)
    # --- sort & filter
    locations = sort_scored_text_vectors(locations)
    locations = filter_text_vectors_within_top_score_diff(locations, 0.05, top_score_position_to_use=1) # skipping position 0 score cause it'll be a tight match and we eval others against highest score
    # RESPONSE
    print('INFO (search_for_locations_by_vector.py): locations', locations)
    return locations
  

# RUN
if __name__ == '__main__':
    query = input("Enter your question here: ")
    query_vector = gpt_embedding(query)
    search_for_locations_by_text_embedding(query_vector)