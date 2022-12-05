from redis import Redis
from rq import Queue

redis_cxn = Redis(host='queue', port=6379)

content_queue = Queue('index_pdf_process_content', connection=redis_cxn)
embeddings_queue = Queue('index_pdf_process_embeddings', connection=redis_cxn)
extractions_queue = Queue('index_pdf_process_extractions', connection=redis_cxn)

default_queue = Queue(connection=redis_cxn)