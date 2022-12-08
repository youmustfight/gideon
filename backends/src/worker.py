from rq import Connection, Worker

# QUEUES
from queues import redis_cxn, indexing_queue, tracking_queue
# PROCESSORS (just importing for file access/reference)
from indexers.processors import *

# WORKER
def start_worker():
    with Connection(redis_cxn):
        print('INFO (worker.py): worker starting on default_queue')
        Worker([
            indexing_queue,
            tracking_queue,
        ]).work()