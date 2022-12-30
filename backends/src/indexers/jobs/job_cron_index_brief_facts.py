import datetime
import sqlalchemy as sa
from dbs.sa_sessions import create_sqlalchemy_session
from indexers.index_brief_facts import index_brief_facts

from dbs.sa_models import Brief

# Schedule to run every ??? minute (see scheduled.py)
async def job_cron_index_brief_facts(job_ctx):
    print('INFO (scheduled_job_index_brief_facts) start')
    session = create_sqlalchemy_session()

    async with session.begin():
        # 1. grab all case facts that have updated (do a 1 min delay so we don't index while users write)
        now = datetime.datetime.now()
        window_end = now - datetime.timedelta(minutes=0)
        window_start = now - datetime.timedelta(minutes=1)
        query_briefs_recently_updated = await session.execute(
            sa.select(Brief).where(sa.and_(Brief.updated_at >= window_start, Brief.updated_at < window_end)))
        briefs_updated = query_briefs_recently_updated.scalars().all()

        # 2. distill down the case ids
        case_ids = list(set(map(lambda br: br.case_id, briefs_updated)))

        # 3. process case facts for each case
        print('INFO (scheduled_job_index_brief_facts) re-index facts for cases:', case_ids)
        for case_id in case_ids:
            await index_brief_facts(session, case_id)
        
        # 4. SAVE!
        await session.commit()

    # Close
    await session.close()