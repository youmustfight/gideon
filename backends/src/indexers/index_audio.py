import numpy as np
import pydash as _
import sqlalchemy as sa
from time import sleep

from dbs.sa_models import Document, DocumentContent, Embedding, File
from dbs.vector_utils import tokenize_string
from files.file_utils import get_file_path, open_txt_file
from files.s3_utils import s3_get_file_url, s3_upload_file
from indexers.utils.extract_document_events import extract_document_events
from models.assemblyai import assemblyai_transcribe
from models.gpt import gpt_completion, gpt_embedding, gpt_summarize, gpt_vars
from models.gpt_prompts import gpt_prompt_document_type

async def _index_audio_process_content(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_audio_process_content) started", document_id)
    # PROCESS FILE + PROPERTIES
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    file = files.first()
    # --- process file for transcript
    transcript_response = assemblyai_transcribe(file.upload_url)
    # DOCUMENT CONTENT CREATION
    # --- chunk audio text: document
    document_text = transcript_response['text']
    document_text_chunks = tokenize_string(document_text, "max_size")
    document_content_text = list(map(lambda chunk: DocumentContent(
        document_id=document_id,
        text=chunk,
        tokenizing_strategy="max_size"
    ), document_text_chunks))
    session.add_all(document_content_text)
    # --- chunk audio text: by sentence (w/ start/end times)
    sentences = transcript_response['sentences']
    document_content_sentences = list(map(lambda sentence: DocumentContent(
        document_id=document_id,
        text=sentence['text'],
        tokenizing_strategy="sentence",
        start_second=sentence['start_second'],
        end_second=sentence['end_second'],
    ), sentences))
    session.add_all(document_content_sentences)
    # SAVE
    document.status_processing_files = "completed"
    document.status_processing_content = "completed"
    session.add(document)

async def _index_audio_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_audio_process_embeddings): start')
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_audio_process_embeddings): document content', document_content)
    # --- CREATE EMBEDDINGS (context is derived from relation)
    for content in list(document_content):
        text_embedding_tensor = gpt_embedding(content.text) # returns numpy array
        text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
        await session.execute(
            sa.insert(Embedding).values(
                document_id=document_id,
                document_content_id=content.id,
                encoded_model="gpt3",
                encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
                encoding_strategy="text",
                vector_json=text_embedding_vector,
            ))
        sleep(gpt_vars()['OPENAI_THROTTLE']) # openai 60 reqs/min
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)

async def _index_audio_process_extractions(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_audio_process_extractions): start')
    # FETCH
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars()
    document_content_text = " ".join(map(
        lambda content: content.text if content.tokenizing_strategy == "max_size" else "", document_content))
    # COMPILE/EXTRACT
    # --- classification/description
    print('INFO (index_pdf.py:_index_audio_process_extractions): document_description')
    document.document_description = gpt_completion(
        gpt_prompt_document_type.replace('<<SOURCE_TEXT>>', document_content_text[0:11_000]),
        max_tokens=75)
    # --- summary
    print('INFO (index_pdf.py:_index_audio_process_extractions): document_summary')
    if len(document_content_text) < 250_000:
        document.document_summary = gpt_summarize(document_content_text, max_length=1500)
    # --- events
    print('INFO (index_pdf.py:_index_audio_process_extractions): document_events')
    document.document_events = await extract_document_events(document_content_text)
    # SAVE
    document.status_processing_extractions = "completed"
    session.add(document)


# INDEX AUDIO
async def index_audio(session, pyfile, case_id) -> int:
    print(f"INFO (index_audio.py): indexing {pyfile.name} ({pyfile.type})")
    try:
        # SETUP DOCUMENT
        document_query = await session.execute(
            sa.insert(Document)
                .values(name=pyfile.name, status_processing_files="queued", type="audio", case_id=case_id)
                .returning(Document.id)) # can't seem to return anything except id
        document_id = document_query.scalar_one_or_none()
        print(f"INFO (index_audio.py): index_document id {document_id}")
        # SAVE & RELATE FILE
        filename = pyfile.name
        upload_key = pyfile.name # TODO: avoid collisions w/ unique prefix
        # --- save to S3
        s3_upload_file(upload_key, pyfile)
        # --- create File()
        input_s3_url = s3_get_file_url(filename)
        session.add(File(
            filename=pyfile.name,
            mime_type=pyfile.type,
            upload_key=upload_key,
            upload_url=input_s3_url,
            document_id=document_id
        ))
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_audio.py): processing file", upload_key)
        await _index_audio_process_content(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): processing embeddings", upload_key)
        await _index_audio_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): processing extractions", upload_key)
        await _index_audio_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_audio.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
