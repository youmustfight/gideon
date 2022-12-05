from redis import Redis
from rq import Connection, Worker
from queues import redis_cxn, default_queue

if __name__ == '__main__':
    with Connection(redis_cxn):
        print('INFO (worker.py): worker starting on default_queue')
        Worker(default_queue).work()
