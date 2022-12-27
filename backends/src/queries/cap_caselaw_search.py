from arq.jobs import JobStatus 
import sqlalchemy as sa
from time import sleep
import requests
from dbs.sa_models import CAPCaseLaw
import env
from caselaw.utils.upsert_caselaw import upsert_caselaw
from worker import create_queue_pool


async def cap_caselaw_search(session, query):
    print('INFO (cap_caselaw_search): query = ', query)
    # Search CAP (w/ full results)
    cap_response = requests.get(
        f'https://api.case.law/v1/cases/',
        params={
            'full_case': 'false',
            'page_size': 10,
            'search': query,
            'ordering': 'relevance',
        },
        headers={ "authorization": f'Token {env.env_get_caselaw_access_project()}', "content-type": "application/json" },
    )
    cap_response = cap_response.json()
    cap_results = cap_response['results']
    print('INFO (cap_caselaw_search): cap_response = ', cap_response)

    # V2 Queue Processing for cases (so we ensure consistent processing/updates)
    arq_pool = await create_queue_pool()    
    arq_jobs = []
    for cap_result in cap_results:
        job = await arq_pool.enqueue_job('job_index_cap_caselaw', cap_result['id'])
        arq_jobs.append(job)
    # --- await results (ids of the cap_case models)
    is_processing_jobs = True
    is_processing_time = 0
    while is_processing_jobs:
        # --- set to false, but...
        is_processing_jobs = False
        # --- set is_processing_true if we have one occurance of != complete
        for job in arq_jobs:
            status = await job.status()
            if status in [JobStatus.deferred, JobStatus.queued, JobStatus.in_progress]: is_processing_jobs = True
        sleep(1)
        is_processing_time += 1
        if (is_processing_time > 30): raise 'CAP Case Query Timeout'

    # --- fetch models from ids
    cap_case_ids = []
    for arq_job in arq_jobs:
        cap_case_ids.append(await arq_job.result())
    query_cap_caselaw = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id.in_(cap_case_ids)))
    cap_cases = query_cap_caselaw.scalars().all()

    # Return
    return cap_cases