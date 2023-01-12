from arq import cron
from arq.connections import RedisSettings
from arq.worker import run_worker
from env import env_queue_host, env_queue_port
from brief.jobs.job_create_case_brief import job_create_case_brief
from caselaw.jobs.job_index_cap_caselaw import job_index_cap_caselaw
from indexers.jobs.job_cron_embeddings_upserter import job_cron_embeddings_upserter
from indexers.jobs.job_cron_index_brief_facts import job_cron_index_brief_facts
from indexers.jobs.job_cron_index_writing import job_cron_index_writing
from indexers.jobs.job_index_document_audio import job_index_document_audio
from indexers.jobs.job_index_document_docx import job_index_document_docx
from indexers.jobs.job_index_document_pdf import job_index_document_pdf
from indexers.jobs.job_index_document_image import job_index_document_image
from indexers.jobs.job_index_document_video import job_index_document_video
from indexers.jobs.job_process_document_extras import job_process_document_extras


# V3 ARQ
# --- worker
def start_worker():
    print('INFO (worker.py:start_worker) start')
    class Settings:
        redis_settings = RedisSettings(host=env_queue_host(), port=env_queue_port())
        job_timeout= 60 * 30 # defaults to 300. we need longer timeouts bc document png processing + embedding can take awhile
        functions = [
            # cron
            job_cron_embeddings_upserter,
            job_cron_index_brief_facts,
            job_cron_index_writing,
            # jobs
            job_create_case_brief,
            job_index_cap_caselaw,
            job_index_document_audio,
            job_index_document_docx,
            job_index_document_image,
            job_index_document_pdf,
            job_index_document_video,
            job_process_document_extras,
        ]
        cron_jobs = [
            # to run each minute, going to say run at second 0
            cron(job_cron_index_brief_facts, unique=True, second=0),
            cron(job_cron_embeddings_upserter, unique=True, second=0),
            cron(job_cron_index_writing, unique=True, second=0),
        ]

    # RUN!
    worker = run_worker(Settings)

