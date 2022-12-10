from time import sleep
from redis import Redis
from rq import Queue

# CONNECTION
redis_cxn = Redis(host='queue', port=6379)

# QUEUES
prompt_queue = Queue('prompt', connection=redis_cxn)
indexing_queue = Queue('indexing', connection=redis_cxn)
tracking_queue = Queue('tracking', connection=redis_cxn)

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