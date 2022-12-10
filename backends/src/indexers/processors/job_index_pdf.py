from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_pdf import index_pdf
from indexers.utils.index_document_content_vectors import index_document_content_vectors

async def job_index_pdf(document_id):
    session = create_sqlalchemy_session()
    # --- process embeddings/extractions
    async with session.begin():
        document_id = await index_pdf(session=session, document_id=document_id)
    # --- queue indexing
    await index_document_content_vectors(session=session, document_id=document_id)
    # --- return
    return document_id