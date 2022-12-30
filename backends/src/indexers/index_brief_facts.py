import sqlalchemy as sa
from sqlalchemy.orm import Session
from agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Brief, Embedding

async def index_brief_facts(session: Session, case_id):
    print(f'INFO (index_brief_facts) start indexing case #{case_id}')
    # FACTS
    # --- Query Facts
    query_brief = await session.execute(
        sa.select(Brief).where(Brief.case_id == int(case_id)))
    case_brief = query_brief.scalars().first()
    # --- Concat facts arr into one string
    facts_string = '\n- '.join(map(lambda cf: cf['text'], case_brief.facts))
    facts_string = f'''Legal Brief Facts:\n\n-{facts_string}'''
    print(f'INFO (index_brief_facts) start indexing case facts: ', facts_string)

    # EMBEDDING
    # --- Create agent
    aiagent_brief_facts_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.brief_facts_similarity_embed, case_id=case_id)
    # --- Encode Text
    brieffact_embeddings = aiagent_brief_facts_embeder.encode_text([facts_string])
    brieffact_embedding = brieffact_embeddings[0]

    # --- Update or Create an Embedding to get Indexed
    query_embedding = await session.execute(
        sa.select(Embedding).where(sa.and_(Embedding.case_id == int(case_id), Embedding.ai_action == aiagent_brief_facts_embeder.ai_action.value)))
    embedding = query_embedding.scalar_one_or_none()
    print(f'INFO (index_brief_facts) existing embedding: ', embedding)

    if embedding != None:
        await session.execute(
            sa.update(Embedding)
                .where(Embedding.id == embedding.id)
                .values(
                    vector_dimensions=len(brieffact_embedding),
                    vector_json=brieffact_embedding.tolist(),
                    indexed_status='queued',
                ))
    else:
        session.add(Embedding(
            case_id=int(case_id),
            encoded_model_engine=aiagent_brief_facts_embeder.model_name,
            encoding_strategy='text',
            vector_dimensions=len(brieffact_embedding),
            vector_json=brieffact_embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
            ai_action=aiagent_brief_facts_embeder.ai_action.value,
            index_id=aiagent_brief_facts_embeder.index_id,
            index_partition_id=aiagent_brief_facts_embeder.index_partition_id,
            indexed_status='queued'
        ))

    # --- Upsert Embedding to Vector DB (Deferred to background job to embed as it goes)
    # TODO: we should always be locked into an index/namespace but will we ever need to delete across others?
    print(f'INFO (index_brief_facts) finished indexing case #{case_id}')
