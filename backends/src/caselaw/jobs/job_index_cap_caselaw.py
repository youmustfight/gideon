from dbs.sa_sessions import create_sqlalchemy_session
from caselaw.index_cap_caselaw import index_cap_caselaw

async def job_index_cap_caselaw(job_ctx, cap_id):
    session = create_sqlalchemy_session()
    # --- process embeddings/extractions
    async with session.begin():
        await index_cap_caselaw(session=session, cap_id=cap_id)
    # --- return
    await session.close()
    return cap_id
