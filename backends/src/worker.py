from arq import create_pool, cron
from arq.connections import RedisSettings
from arq.worker import run_worker
from env import env_queue_host, env_queue_port
from caselaw.jobs.job_index_cap_caselaw import job_index_cap_caselaw
from indexers.jobs.job_cron_embeddings_upserter import job_cron_embeddings_upserter
from indexers.jobs.job_cron_index_legal_brief_facts import job_cron_index_legal_brief_facts
from indexers.jobs.job_cron_index_writing import job_cron_index_writing
from indexers.jobs.job_index_document_audio import job_index_document_audio
from indexers.jobs.job_index_document_pdf import job_index_document_pdf
from indexers.jobs.job_index_document_image import job_index_document_image
from indexers.jobs.job_index_document_video import job_index_document_video

# V3 ARQ
# --- queue creator
async def create_queue_pool():
    return await create_pool(RedisSettings(host=env_queue_host(), port=env_queue_port()))

# --- worker
def start_worker():
    print('INFO (worker.py:start_worker) start')
    class Settings:
        redis_settings = RedisSettings(host=env_queue_host(), port=env_queue_port())
        functions = [
            # cron
            job_cron_embeddings_upserter,
            job_cron_index_legal_brief_facts,
            job_cron_index_writing,
            # jobs
            job_index_cap_caselaw,
            job_index_document_audio,
            job_index_document_image,
            job_index_document_pdf,
            job_index_document_video,
        ]
        cron_jobs = [
            # to run each minute, going to say run at second 0
            cron(job_cron_index_legal_brief_facts, unique=True, second=0),
            cron(job_cron_embeddings_upserter, unique=True, second=0),
            cron(job_cron_index_writing, unique=True, second=0),
        ]

    # RUN!
    worker = run_worker(Settings)

