from redis import Redis
from rq import Queue

# CONNECTION
redis_cxn = Redis(host='queue', port=6379)

# QUEUES
indexing_queue = Queue('indexing', connection=redis_cxn)
tracking_queue = Queue('tracking', connection=redis_cxn)
