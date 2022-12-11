from time import sleep
from redis import Redis
from rq import Queue

# CONNECTION
redis_cxn = Redis(host='queue', port=6379)

# QUEUES
# --- common props? (https://python-rq.org/docs/#enqueueing-jobs)
MAX_QUEUED_SECONDS = 60 * 60 * 24 * 3 # 3 days
JOB_TIMEOUT_SECONDS = 60 * 10 # 10 min
# --- init
prompt_queue = Queue('prompt', connection=redis_cxn, ttl=MAX_QUEUED_SECONDS, job_timeout=JOB_TIMEOUT_SECONDS)
indexing_queue = Queue('indexing', connection=redis_cxn, ttl=MAX_QUEUED_SECONDS, job_timeout=JOB_TIMEOUT_SECONDS)
tracking_queue = Queue('tracking', connection=redis_cxn, ttl=MAX_QUEUED_SECONDS, job_timeout=JOB_TIMEOUT_SECONDS)

# HELPERS
def await_enqueued_results(jobs):
    print('INFO (queues.py:await_enqueued_results) start...', jobs)
    all_jobs_done = False
    while all_jobs_done == False:
        jobs_results = list(map(lambda j: j.result, jobs))
        all_jobs_done = None not in jobs_results
        print('INFO (queues.py:await_enqueued_results) polling results...', jobs_results)
        sleep(1)
    return jobs_results