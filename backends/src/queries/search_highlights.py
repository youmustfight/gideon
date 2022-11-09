import openai
from env import env_get_open_ai_api_key
from models.gpt import gpt_embedding
from dbs.vector_utils import similarity
# DEPRECATED: from gideon_search import filter_text_vectors_within_top_score_diff, search_similar_file_text_vectors, sort_scored_text_vectors

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()


# SEARCH QUERY
def search_highlights(query):
    print('INFO (search_highlights.py): query all highlights with query "{query}"'.format(query=query))
    # SETUP
    # --- files
    json_highlights = [] # get_highlights_json()
    highlights = []
    # --- get query embed for similarity scoring
    query_vector = gpt_embedding(query)
    
    # VECTOR SIMILARITY SCORING
    # --- for each file
    for json_highlight_payload in json_highlights:
      # --- score highlight
      json_highlight_payload['highlight_score'] = similarity(query_vector, json_highlight_payload['highlight_text_vector'])
      # --- score note
      json_highlight_payload['note_score'] = similarity(query_vector, json_highlight_payload['note_text_vector'])
      # --- set 'score' to whatever was highest for easy sorting/filtering
      json_highlight_payload['score'] = json_highlight_payload['highlight_score'] if json_highlight_payload['highlight_score'] > json_highlight_payload['note_score'] else json_highlight_payload['note_score']
      # -- append
      highlights.append(json_highlight_payload)
    # --- sort & filter
    # highlights = sort_scored_text_vectors(highlights)
    # highlights = filter_text_vectors_within_top_score_diff(highlights, 0.2) # be looser w/ this score?
    
    # RESPONSE
    print('INFO (search_highlights.py): highlights', highlights)
    return highlights
