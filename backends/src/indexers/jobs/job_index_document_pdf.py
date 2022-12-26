from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_document_pdf import index_document_pdf

async def job_index_document_pdf(job_ctx, document_id):
    session = create_sqlalchemy_session()
    # --- process embeddings/extractions
    async with session.begin():
        document_id = await index_document_pdf(session=session, document_id=document_id)
    # --- return
    return document_id
