from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_image import index_image
from indexers.utils.upsert_document_content_vectors import upsert_document_content_vectors

async def job_index_image(document_id):
    session = create_sqlalchemy_session()
    # --- process embeddings/extractions
    async with session.begin():
        document_id = await index_image(session=session, document_id=document_id)
    # --- queue indexing
    await upsert_document_content_vectors(session=session, document_id=document_id)
    # --- return
    return document_id