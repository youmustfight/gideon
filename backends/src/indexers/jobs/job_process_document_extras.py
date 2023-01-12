from dbs.sa_sessions import create_sqlalchemy_session
from indexers.process_document_extras import process_document_extras

async def job_process_document_extras(job_ctx, document_id):
    session = create_sqlalchemy_session()

    # --- process embeddings/extractions
    async with session.begin():
        document_id = await process_document_extras(session=session, document_id=document_id)

    # --- return
    return document_id
