from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_document_image import index_document_image
from arq_queue.create_queue_pool import create_queue_pool

async def job_index_document_image(job_ctx, document_id):
    session = create_sqlalchemy_session()

    # --- process embeddings/extractions
    async with session.begin():
        document_id = await index_document_image(session=session, document_id=document_id)

    # --- trigger longer running extractions job
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_process_document_extras', document_id)

    # --- return
    return document_id