import sqlalchemy as sa
from sqlalchemy.orm import Session
from agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import LegalBriefFact, Embedding

async def index_legal_brief_facts(session: Session, case_id):
    print(f'INFO (index_legal_brief_facts) start indexing case #{case_id}')
    # FACTS
    # --- Query Facts
    query_legal_brief_facts = await session.execute(
        sa.select(LegalBriefFact).where(LegalBriefFact.case_id == int(case_id)))
    legal_brief_facts = query_legal_brief_facts.scalars().all()
    # --- Concat into one string
    facts_string = "\n".join(map(lambda cf: cf.text, legal_brief_facts))
    print(f'INFO (index_legal_brief_facts) start indexing case facts: ', facts_string)

    # EMBEDDING
    # --- Create agent
    aiagent_legal_brief_facts_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.legal_brief_facts_similarity_embed, case_id=case_id)
    # --- Encode Text
    legal_brief_fact_embeddings = aiagent_legal_brief_facts_embeder.encode_text([facts_string])
    legal_brief_fact_embedding = legal_brief_fact_embeddings[0]

    # --- Update or Create an Embedding to get Indexed
    query_embedding = await session.execute(
        sa.select(Embedding).where(sa.and_(Embedding.case_id == int(case_id), Embedding.ai_action == aiagent_legal_brief_facts_embeder.ai_action.value)))
    embedding = query_embedding.scalar_one_or_none()
    print(f'INFO (index_legal_brief_facts) existing embedding: ', embedding)

    if embedding != None:
        await session.execute(
            sa.update(Embedding)
                .where(Embedding.id == embedding.id)
                .values(
                    vector_dimensions=len(legal_brief_fact_embedding),
                    vector_json=legal_brief_fact_embedding.tolist(),
                    indexed_status='queued',
                ))
    else:
        session.add(Embedding(
            case_id=int(case_id),
            encoded_model_engine=aiagent_legal_brief_facts_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(legal_brief_fact_embedding),
            vector_json=legal_brief_fact_embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
            ai_action=aiagent_legal_brief_facts_embeder.ai_action.value,
            index_id=aiagent_legal_brief_facts_embeder.index_id,
            index_partition_id=aiagent_legal_brief_facts_embeder.index_partition_id,
            indexed_status='queued'
        ))

    # --- Upsert Embedding to Vector DB (Deferred to background job to embed as it goes)
    # TODO: we should always be locked into an index/namespace but will we ever need to delete across others?
    print(f'INFO (index_legal_brief_facts) finished indexing case #{case_id}')
