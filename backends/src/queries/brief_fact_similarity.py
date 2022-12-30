import sqlalchemy as sa
from agents.ai_action_agent import AI_ACTIONS, create_ai_action_agent
from dbs.sa_models import Case, Embedding
from dbs.vectordb_pinecone import get_embeddings_from_search_vectors
from logger import logger
from queries.utils.location_from_search_vector_embedding import location_from_search_vector_embedding

async def brief_fact_similarity(session, case_id, organization_id, query_text=None):
    logger.info(f'brief_fact_similarity')
    # 0. SETUP
    # --- get case ids we want to search against TODO: handle org<>case or user<>case filter but for now we just grabbing all cases
    query_cases = await session.execute(
        sa.select(Case)
            .where(Case.organization_id == organization_id))
    case_ids = list(map(lambda c: int(c.id), query_cases.scalars().all()))

    # --- get vector to do check with
    aigent_fact_embedder = await create_ai_action_agent(session, action=AI_ACTIONS.brief_facts_similarity_embed, case_id=case_id, organization_id=organization_id)
    legal_brief_fact_vectors = None
    # --- if text.... embed newly
    if query_text != None:
        legal_brief_fact_vectors = aigent_fact_embedder.encode_text([query_text])
    # --- if case_id present... grab from db
    elif case_id != None:
        query_fact_embedding = await session.execute(
            sa.select(Embedding).where(
                sa.and_(
                    Embedding.case_id == int(case_id),
                    Embedding.ai_action == AI_ACTIONS.brief_facts_similarity_embed.value)))
        legal_brief_fact_embedding = query_fact_embedding.scalar_one_or_none()
        legal_brief_fact_vectors = [legal_brief_fact_embedding.vector_json]

    # 1. SEARCH
    # --- similarity search
    aigent_fact_similarity = await create_ai_action_agent(session, action=AI_ACTIONS.brief_facts_similarity_search, case_id=case_id, organization_id=organization_id)
    query_filters = { 'case_id': { '$in': case_ids } }
    if case_id != None:
        query_filters['case_id'].update({ '$ne': case_id })
    lbf_search_vectors = aigent_fact_similarity.index_query(
        query_vectors=legal_brief_fact_vectors,
        query_filters=query_filters,
        top_k=10,
        score_max=1,
        # every legal brief is a similar structure, so trying high strictness
        score_max_diff_percent=0.05, 
        score_min=0.8)
    lbf_search_embeddings = await get_embeddings_from_search_vectors(session, lbf_search_vectors)

    # 2. Maps
    logger.info(f"search_embeddings count: {len(lbf_search_embeddings)}")
    # --- search vectors
    locations = list(map(lambda sv: location_from_search_vector_embedding(sv, lbf_search_embeddings), lbf_search_vectors))
    locations = list(filter(lambda loc: loc != None, locations))

    # 3. RETURN (serialized?)
    logger.info(f"locations count: {len(locations)}")
    return locations