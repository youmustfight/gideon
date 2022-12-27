from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_document_audio import index_document_audio

async def job_index_document_audio(job_ctx, document_id):
    session = create_sqlalchemy_session()
    
    # --- process embeddings/extractions
    async with session.begin():
        document_id = await index_document_audio(session=session, document_id=document_id)

    # --- return
    await session.close()
    return document_id