from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Session
from agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Writing, Embedding

async def index_writing(session: Session, writing_id):
    print(f'INFO (index_writing) start indexing writing #{writing_id}')
    # FACTS
    # --- Query writing
    query_writing = await session.execute(
        sa.select(Writing).where(Writing.id == int(writing_id)))
    writing: Writing = query_writing.scalars().one()
    print(f'INFO (index_writing) writing text: ', writing.body_text)

    # EMBEDDING (DOING EMBEDDING OF ALL TEXT)
    # --- Create agent
    # TODO SENTENCE LEVEL
    # TODO GET ACTION LOCKS FOR ORG, SO WE CAN SEARCH TEMPLATES
    aiagent_writing_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.writing_similarity_embed, case_id=writing.case_id, organization_id=writing.organization_id)
    # --- Encode Text
    writing_embeddings = aiagent_writing_embeder.encode_text([writing.body_text])
    writing_embedding = writing_embeddings[0]

    # --- Update or Create an Embedding to get Indexed
    query_embedding = await session.execute(
        sa.select(Embedding).where(sa.and_(Embedding.writing_id == int(writing_id), Embedding.ai_action == aiagent_writing_embeder.ai_action.value)))
    embedding = query_embedding.scalar_one_or_none()
    print(f'INFO (index_writing) existing embedding: ', embedding)

    if embedding != None:
        await session.execute(
            sa.update(Embedding)
                .where(Embedding.id == embedding.id)
                .values(
                    vector_dimensions=len(writing_embedding),
                    vector_json=writing_embedding.tolist(),
                    indexed_status='queued',
                ))
    else:
        session.add(Embedding(
            case_id=writing.case_id,
            writing_id=writing.id,
            encoded_model_engine=aiagent_writing_embeder.model_name,
            encoding_strategy='text',
            vector_dimensions=len(writing_embedding),
            vector_json=writing_embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
            ai_action=aiagent_writing_embeder.ai_action.value,
            index_id=aiagent_writing_embeder.index_id,
            index_partition_id=aiagent_writing_embeder.index_partition_id,
            indexed_status='queued',
            created_at=datetime.now(),
        ))

    # --- Upsert Embedding to Vector DB (Deferred to background job to embed as it goes)
    # TODO: we should always be locked into an index/namespace but will we ever need to delete across others?
    print(f'INFO (index_writing) finished indexing writing #{writing_id}')
