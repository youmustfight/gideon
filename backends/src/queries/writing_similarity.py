from agents.ai_action_agent import AI_ACTIONS, create_ai_action_agent
from dbs.vectordb_pinecone import get_embeddings_from_search_vectors
from logger import logger
from queries.utils.location_from_search_vector_embedding import location_from_search_vector_embedding

async def writing_similarity(session, query: str, organization_id=None):
    logger.info(f'writing_similarity')
    # 1. SEARCH
    aigent_writing_similarity = await create_ai_action_agent(session, action=AI_ACTIONS.writing_similarity_search, organization_id=organization_id)
    # --- encodings don't need to happen here, we can let our index_query helper do it
    # --- setup filters
    wr_filters = {}
    if organization_id: wr_filters.update({ 'organization_id': { '$eq': organization_id } })
    # --- query
    wr_search_vectors = aigent_writing_similarity.index_query(
        query_text=query,
        query_filters=wr_filters,
        top_k=10,
        score_max=1,
        score_max_diff_percent=0.05, 
        score_min=0.6)
    wr_search_embeddings = await get_embeddings_from_search_vectors(session, wr_search_vectors)

    # 3. MAP
    logger.info(f"search_embeddings count: {len(wr_search_embeddings)}")
    # --- search vectors
    locations = list(map(lambda sv: location_from_search_vector_embedding(sv, wr_search_embeddings), wr_search_vectors))
    locations = list(filter(lambda loc: loc != None, locations))

    # 4. RETURN
    logger.info(f"locations count: {len(locations)}")
    return locations
