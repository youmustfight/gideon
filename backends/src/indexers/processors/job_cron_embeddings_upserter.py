from datetime import datetime
from typing import List
import pinecone
import pydash as _
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from dbs.sa_sessions import create_sqlalchemy_session
from dbs.sa_models import Document, DocumentContent, Embedding

# Schedule to run every ??? minute (see scheduled.py)
async def job_cron_embeddings_upserter(job_ctx):
    print('INFO (scheduled_job_embeddings_upserter) start')
    session = create_sqlalchemy_session()
    
    # 1. Fetch Embeddings
    query_embeddings = await session.execute(
        sa.select(Embedding).options(
            joinedload(Embedding.case),
            joinedload(Embedding.document_content).options(
                joinedload(DocumentContent.document).options(
                    joinedload(Document.case)
                )
            )
        ).where(Embedding.indexed_status == 'queued'))
    embeddings: List[Embedding] = query_embeddings.scalars().all()

    # setup dict, where tuple is (index, partition)
    upserts_tuple_dict = {}
    # 2. For each embedding, setup the upsert record for each index/partition(aka namespace in pinecone db)
    for embedding in embeddings:
        # --- get relations
        em = embedding
        dc = embedding.document_content
        cs = embedding.case or embedding.document_content.document.case
        # --- setup metadata (do getter checks bc None type gives API errors w/ pinecone)
        metadata = {
            "case_id": cs.id,
            "case_uuid": str(cs.uuid), # casting bc UUID class -> str
            "embedding_id": em.id, # just in case at some point we can't use vector id
        }
        if _.get(dc, 'document_id'): metadata['document_id'] = dc.document_id
        if em.writing_id: metadata['writing_id'] = em.writing_id
        # --- form upsert
        upsert_record = (str(em.id), em.vector_json, metadata)
        print('INFO (scheduled_job_embeddings_upserter) upsert_record:', (upsert_record[0], upsert_record[2]))
        # --- add to tuple dict so we can batch insert
        if (upserts_tuple_dict.get((embedding.index_id, embedding.index_partition_id)) == None):
            upserts_tuple_dict[(embedding.index_id, embedding.index_partition_id)] = [upsert_record]
        else:
            upserts_tuple_dict[(embedding.index_id, embedding.index_partition_id)].append(upsert_record)

    # Upsert by index/partition (http calls to pinecone are incredibly slow if done individually)
    for index_tuple in upserts_tuple_dict:
        # --- upsert records to pinecone db
        pinecone.Index(index_name=index_tuple[0]).upsert(
            vectors=upserts_tuple_dict[index_tuple],
            namespace=index_tuple[1])
        # --- update embedding indexd_status = 'completed'
        embedding_ids = list(map(lambda upsert_tuple: int(upsert_tuple[0]), upserts_tuple_dict[index_tuple]))
        print('INFO (scheduled_job_embeddings_upserter) embedding_ids upserted:', embedding_ids)
        await session.execute(
            sa.update(Embedding)
                .where(Embedding.id.in_(embedding_ids))
                .values(indexed_status='completed',updated_at=datetime.now()))
        # --- commit after each batch in case one fails
        await session.commit()

    print('INFO (scheduled_job_embeddings_upserter) done')