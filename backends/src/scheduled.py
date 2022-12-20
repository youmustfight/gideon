import schedule
import time
from indexers.processors.scheduled_job_embeddings_upserter import scheduled_job_embeddings_upserter
from indexers.processors.scheduled_job_index_legal_brief_facts import scheduled_job_index_legal_brief_facts
from queues import indexing_queue

# HACK: this should be a well integrated option of our worker/queue lib. rq doesn't support crontab yet, and celery+arq were beconing an immense pain
# Provided unique 'job_id' to ensure multiple workers don't queue the same job
def start_scheduled():
  print("INFO (start_scheduled) start")
  # --- Embeddings
  schedule.every(1).minute.do(lambda: indexing_queue.enqueue(
    scheduled_job_embeddings_upserter,
    job_id="scheduled_job_embeddings_upserter"))
  # --- Legal Brief Facts
  schedule.every(1).minute.do(lambda: indexing_queue.enqueue(
    scheduled_job_index_legal_brief_facts,
    job_id="scheduled_job_index_legal_brief_facts"))

  # RUN
  while True:
    schedule.run_pending()
    time.sleep(5)
