import sqlalchemy as sa
from dbs.sa_models import Brief
from dbs.sa_sessions import create_sqlalchemy_session
from brief.create_case_brief import create_case_brief

async def job_create_case_brief(job_ctx, case_id, issues):
    session = create_sqlalchemy_session()
    async with session.begin():
        # if a brief exists, delete it
        await session.execute(sa.delete(Brief)
            .where(Brief.case_id == int(case_id)))
        # genereate brief
        brief = await create_case_brief(session, case_id=int(case_id), issues=issues)
        # save brief
        session.add(brief)
    # --- return
    await session.close()
    return case_id
