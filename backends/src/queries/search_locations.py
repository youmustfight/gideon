from queries.utils.search_vector_to_location import search_vector_to_location
from aia.agent import AI_ACTIONS, create_ai_action_agent
from dbs.vectordb_pinecone import get_embeddings_from_search_vectors


async def search_locations(session, query_text, case_id):
    print(f"INFO (search_locations.py): query all documents via '{query_text}'")
    # 1. SEARCH & SERIALIZE
    # --- pdfs/transcripts
    aigent_location_text_searcher = await create_ai_action_agent(session, action=AI_ACTIONS.case_similarity_text_sentence_search, case_id=case_id)
    text_search_vectors = aigent_location_text_searcher.query_search_vectors(
        query_text,
        query_filters={ "string_length": { "$gt": 80 } }, # ensure a minimum
        top_k=10,
        score_max=1,
        score_max_diff_percent=0.2,
        score_min=0.3)
    text_search_embeddings = await get_embeddings_from_search_vectors(session, text_search_vectors)

    # --- images (including video frames)
    aigent_location_image_searcher = await create_ai_action_agent(session, action=AI_ACTIONS.case_similarity_text_to_image_search, case_id=case_id)
    image_search_vectors = aigent_location_image_searcher.query_search_vectors(
        query_text,
        top_k=5,
        score_max=1,
        score_min=0.15)
    image_search_embeddings = await get_embeddings_from_search_vectors(session, image_search_vectors)
    
    # 2. Combine
    search_vectors = text_search_vectors + image_search_vectors
    search_embeddings = text_search_embeddings + image_search_embeddings
    print(f"INFO (search_locations.py): search_embeddings", search_embeddings)
    locations = list(map(lambda sv: search_vector_to_location(sv, search_embeddings), search_vectors))
    locations = list(filter(lambda loc: loc != None, locations))

    # 3. RETURN (serialized?)
    print(f"INFO (search_locations.py): locations", len(locations))
    return locations
