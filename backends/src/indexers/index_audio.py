import pydash as _
import sqlalchemy as sa
from agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner
from indexers.utils.tokenize_string import TOKENIZING_STRATEGY
from models.assemblyai import assemblyai_transcribe
from models.gpt import gpt_completion, gpt_summarize
from models.gpt_prompts import gpt_prompt_document_type

async def _index_audio_process_content(session, document_id: int) -> None:
    print("INFO (index_pdf.py:_index_audio_process_content) started", document_id)
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()

    if len(document_content) == 0:
        # 1. AUDIO -> TEXT (SENTENCES)
        files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
        files = files_query.scalars()
        file = files.first()
        # --- process file for transcript
        transcript_response = assemblyai_transcribe(file.upload_url)
        sentences = transcript_response['sentences']
        # 2. DOCUMENT CONTENT CREATION
        # --- 2a. Tokenize/process text by sentence
        document_content_sentences = []
        counter_sentences = 0
        for sentence in sentences:
            counter_sentences += 1
            document_content_sentences.append(DocumentContent(
                document_id=document_id,
                text=sentence['text'],
                tokenizing_strategy=TOKENIZING_STRATEGY.sentence.value,
                second_start=sentence['second_start'],
                second_end=sentence['second_end'],
                sentence_number=counter_sentences,
            ))
        session.add_all(document_content_sentences)
        # --- 2b. Tokenize/process text by max size
        document_content_sentence_chunks = _.chunk(document_content_sentences, 20)
        document_content_sentences_20 = []
        for dcsc in document_content_sentence_chunks:
            sentence_start = dcsc[0].sentence_number
            sentence_end = dcsc[-1].sentence_number
            second_start = dcsc[0].second_start
            second_end = dcsc[-1].second_end
            document_content_sentences_20.append(DocumentContent(
                document_id=document_id,
                text=' '.join(map(lambda dc: dc.text, dcsc)),
                tokenizing_strategy=TOKENIZING_STRATEGY.sentences_20.value,
                sentence_start=sentence_start,
                sentence_end=sentence_end,
                second_start=second_start,
                second_end=second_end
            ))
        session.add_all(document_content_sentences_20)
        print(f"INFO (index_pdf.py:_index_audio_process_content): Inserted new document content records")
    else:
        print(f"INFO (index_pdf.py:_index_audio_process_content): already processed content for document #{document_id} (content count: {len(document_content)})")

    # 3. SAVE
    document.status_processing_content = "completed"
    session.add(document)
    print("INFO (index_pdf.py:_index_audio_process_content) done", document_id)

async def _index_audio_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_audio_process_embeddings): start')
    # SETUP
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_audio_process_embeddings): document content', document_content)
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value, document_content))
    document_content_sentences_20 = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentences_20.value, document_content))
    # CREATE EMBEDDINGS (context is derived from relation)
    # --- agents
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id)
    aiagent_sentences_20_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentences_20_embed, case_id=document.case_id)
    # --- sentences (batch processing to avoid rate limits/throttles)
    print('INFO (index_pdf.py:_index_audio_process_embeddings): encoding sentences...', document_content_sentences)
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
    # --- batch sentences (batch processing to avoid rate limits/throttles)
    print('INFO (index_pdf.py:_index_audio_process_embeddings): encoding sentences in chunks of 20...', document_content_sentences_20)
    sentences_20_embeddings = aiagent_sentences_20_embeder.encode_text(list(map(lambda c: c.text, document_content_sentences_20)))
    sentences_20_embeddings_as_models = []
    for index, embedding in enumerate(sentences_20_embeddings):
        sentences_20_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=document_content_sentences_20[index].id,
            encoded_model_engine=aiagent_sentences_20_embeder.model_name,
            encoding_strategy="text",
            vector_dimensions=len(embedding),
            vector_json=embedding.tolist(),
        ))
    session.add_all(sentences_20_embeddings_as_models)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)
    print('INFO (index_pdf.py:_index_audio_process_embeddings): done')

async def _index_audio_process_extractions(session, document_id: int) -> None:
    print('INFO (index_pdf.py:_index_audio_process_extractions): start')
    # FETCH
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars()
    document_content_text = " ".join(map(
        lambda content: content.text if content.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value else "", document_content))
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
        document.document_summary_one_liner = extract_document_summary_one_liner(document.document_summary)
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
