import datetime
import sqlalchemy as sa
from dbs.sa_sessions import create_sqlalchemy_session
from dbs.sa_models import Writing
from indexers.index_writing import index_writing

# Schedule to run every ??? minute (see scheduled.py)
async def job_cron_index_writing(job_ctx):
    print('INFO (scheduled_job_index_writing) start')
    session = create_sqlalchemy_session()

    async with session.begin():
        # 1. grab all case facts that have updated (do a 1 min delay so we don't index while users write)
        now = datetime.datetime.now()
        window_end = now - datetime.timedelta(minutes=0)
        window_start = now - datetime.timedelta(minutes=1)
        query_writings_recently_updated = await session.execute(
            sa.select(Writing).where(sa.and_(Writing.updated_at >= window_start, Writing.updated_at < window_end)))
        writings_updated = query_writings_recently_updated.scalars().all()

        # 2. distill down the case ids
        writing_ids = list(set(map(lambda wr: wr.id, writings_updated)))

        # 3. process case facts for each case
        print('INFO (scheduled_job_index_writing) re-index writings:', writing_ids)
        for writing_id in writing_ids:
            await index_writing(session, writing_id)

        # 4. SAVE!
        await session.commit()
