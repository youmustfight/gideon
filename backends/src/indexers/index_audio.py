import numpy as np
import pydash as _
import sqlalchemy as sa
from time import sleep

from aia.agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from dbs.vector_utils import tokenize_string
from files.file_utils import get_file_path, open_txt_file
from files.s3_utils import s3_get_file_url, s3_upload_file
from indexers.utils.extract_document_events import extract_document_events_v1
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
    document.status_processing_content = "completed"
    session.add(document)

async def _index_audio_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_audio_process_embeddings): start')
    # SETUP
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_audio_process_embeddings): document content', document_content)
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == "sentence", document_content))
    document_content_maxed_size = list(filter(lambda c: c.tokenizing_strategy == "max_size", document_content))
    # CREATE EMBEDDINGS (context is derived from relation)
    # --- agents
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id)
    aiagent_max_size_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_max_size_embed, case_id=document.case_id)
    # --- sentences (batch processing to avoid rate limits/throttles)
    sentence_embeddings = aiagent_sentence_embeder.encode_text(list(map(lambda c: c.text, document_content_sentences)))
    sentence_embeddings_as_models = []
    for index, embedding in enumerate(sentence_embeddings):
        sentence_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_sentences[index].id,
            encoded_model_engine=aiagent_sentence_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
        ))
    session.add_all(sentence_embeddings_as_models)
    # --- max_size (batch processing to avoid rate limits/throttles)
    for content in list(document_content):
        text_embedding_tensor = gpt_embedding(content.text) # returns numpy array
        text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
        await session.execute(
            sa.insert(Embedding).values(
                document_id=document_id,
                document_content_id=content.id,
                encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
                encoding_strategy="text",
                vector_json=text_embedding_vector,
            ))
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
    document.document_events = await extract_document_events_v1(document_content_text)
    # SAVE
    document.status_processing_extractions = "completed"
    session.add(document)


# INDEX AUDIO
async def index_audio(session, document_id) -> int:
    print(f"INFO (index_audio.py): indexing document #{document_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_audio.py): processing document #{document_id} content")
        await _index_audio_process_content(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): processing document #{document_id} embeddings")
        await _index_audio_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): processing document #{document_id} extractions")
        await _index_audio_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_audio.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_audio.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
