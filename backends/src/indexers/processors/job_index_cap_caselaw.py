from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_cap_caselaw import index_cap_caselaw
from indexers.utils.upsert_document_content_vectors import upsert_document_content_vectors

async def job_index_cap_caselaw(cap_id):
    session = create_sqlalchemy_session()
    # --- process embeddings/extractions
    async with session.begin():
        cap_caselaw_id = await index_cap_caselaw(session=session, cap_id=cap_id)
    # --- return
    return cap_caselaw_id
