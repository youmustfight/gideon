import logging
from rq import Connection, Worker

# QUEUES
from queues import redis_cxn, indexing_queue, prompt_queue, tracking_queue
# PROCESSORS (just importing for file access/reference)
from indexers.processors import *
from queries.processors import *

# WORKER
def start_worker():
    with Connection(redis_cxn):
        Worker([
            indexing_queue,
            prompt_queue,
            tracking_queue,
        ]).work()
