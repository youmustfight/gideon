import asyncio
import io
import mammoth
import pydash as _
import requests
import sqlalchemy as sa
from ai.agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from indexers.utils.extract_document_type import extract_document_type
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner
from indexers.utils.tokenize_string import tokenize_string, TOKENIZING_STRATEGY


async def _index_document_docx_process_content(session, document_id: int) -> None:
    print("INFO (index_document_docx.py:_index_document_docx_process_content) started", document_id)
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    file = files_query.scalars().first()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()

    if len(document_content) == 0:
        # 1. DOCX -> HTML -> TEXT (SENTENCES)
        print(f"INFO (index_document_docx.py:_index_document_docx_process_content): converting {file.filename} to text")
        # --- request gives response via .raw property, which we read() for bytes, which we pass to BytesIO to give us back an 'opened file'
        docx_bytes = io.BytesIO(requests.get(file.upload_url, stream=True).raw.read())
        docx_text_raw = mammoth.extract_raw_text(docx_bytes) # TODO: if we want to extract html, we can
        docx_text = docx_text_raw.value.encode(encoding='ASCII',errors='ignore').decode() # The raw text w/ unicode clean up. should we do more widely?
        print(f'INFO (index_document_docx.py:_index_document_docx_process_content): docx_text', docx_text)
        # 2. DOCUMENT CONTENT CREATE
        # --- 2b. Tokenize/process text by sentence
        document_content_sentences = []
        counter_sentences = 0
        docx_text_sentences = tokenize_string(docx_text, TOKENIZING_STRATEGY.sentence.value)
        for sentence in docx_text_sentences:
            counter_sentences += 1
            document_content_sentences.append(DocumentContent(
                document_id=document_id,
                text=sentence,
                tokenizing_strategy=TOKENIZING_STRATEGY.sentence.value,
                sentence_number=counter_sentences,
            ))
        session.add_all(document_content_sentences)
        # --- 2c. Tokenize/process text by batches (defined by text-similiarty-davinci-001, should later try chunking by # sentences)
        document_content_sentence_chunks = _.chunk(document_content_sentences, 20)
        document_content_sentences_20 = []
        for dcsc in document_content_sentence_chunks:
            sentence_start = dcsc[0].sentence_number
            sentence_end = dcsc[-1].sentence_number
            document_content_sentences_20.append(DocumentContent(
                document_id=document_id,
                text=' '.join(map(lambda dc: dc.text, dcsc)),
                tokenizing_strategy=TOKENIZING_STRATEGY.sentences_20.value,
                sentence_start=sentence_start,
                sentence_end=sentence_end
            ))
        session.add_all(document_content_sentences_20)
        print(f"INFO (index_document_docx.py:_index_document_docx_process_content): Inserted new document content records")
    else:
        print(f"INFO (index_document_docx.py:_index_document_docx_process_content): already processed content for document #{document_id} (content count: {len(document_content)})")

    # 3. SAVE
    document.status_processing_content = "completed"
    session.add(document) # if modifying a record/model, we can use add() to do an update
    print('INFO (index_document_docx.py:_index_document_docx_process_content): done')

async def _index_document_docx_process_embeddings(session, document_id: int) -> None:
    print('INFO (index_document_docx.py:_index_document_docx_process_embeddings): start')
    # SETUP
    # --- documents
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = list(document_content_query.scalars().all())
    print('INFO (index_document_docx.py:_index_document_docx_process_embeddings): # of document content', len(document_content))
    document_content_sentences = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value, document_content))
    document_content_sentences_20 = list(filter(lambda c: c.tokenizing_strategy == TOKENIZING_STRATEGY.sentences_20.value, document_content))
    # V2 CREATE EMBEDDINGS
    # --- session/agent
    aiagent_sentence_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=document.case_id, user_id=document.user_id)
    aiagent_sentences_20_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentences_20_embed, case_id=document.case_id, user_id=document.user_id)
    # --- sentences (sentence-transformer = free, but very limited token length)
    print('INFO (index_document_docx.py:_index_document_docx_process_embeddings): encoding sentences...', document_content_sentences)
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
            ai_action=aiagent_sentence_embeder.ai_action.value,
            index_id=aiagent_sentence_embeder.index_id,
            index_partition_id=aiagent_sentence_embeder.index_partition_id,
            indexed_status='queued'
        ))
    session.add_all(sentence_embeddings_as_models)
    # --- batches (gpt3 ada = very very cheap, and large token length)
    print('INFO (index_document_docx.py:_index_document_docx_process_embeddings): encoding sentences in chunks of 20...', document_content_sentences_20)
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
            ai_action=aiagent_sentences_20_embeder.ai_action.value,
            index_id=aiagent_sentences_20_embeder.index_id,
            index_partition_id=aiagent_sentences_20_embeder.index_partition_id,
            indexed_status='queued'
        ))
    session.add_all(sentences_20_embeddings_as_models)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)
    print('INFO (index_document_docx.py:_index_document_docx_process_embeddings): done')

async def _index_document_docx_process_extractions(session, document_id: int) -> None:
    print('INFO (index_document_docx.py:_index_document_docx_process_extractions): start')
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(
        sa.select(DocumentContent)
            .where(DocumentContent.document_id == document_id)
            .where(DocumentContent.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value))
    document_content_sentences = document_content_query.scalars()
    document_content_text = " ".join(map(lambda content: content.text, document_content_sentences))
    print(f'INFO (index_document_docx.py:_index_document_docx_process_extractions): len(document_text) = {len(document_content_text)}')
    # EXTRACT
    # --- classification/description
    print('INFO (index_document_docx.py:_index_document_docx_process_extractions): document_description')
    document.generated_description = extract_document_type(document_content_text)
    # --- summary
    print('INFO (index_document_docx.py:_index_document_docx_process_extractions): document_summary')
    if len(document_content_text) < 250_000:
        document.generated_summary = extract_document_summary(document_content_text)
        document.generated_summary_one_liner = extract_document_summary_one_liner(document.generated_summary)
    else:
        print('INFO (index_document_docx.py:_index_document_docx_process_extractions): document is too long')
    # --- cases/laws mentioned
    #  TODO: await extract_document_caselaw_mentions(document_content_text)
    # --- event timeline v2
    print('INFO (index_document_docx.py:_index_document_docx_process_extractions): events')
    # document.genereated_events = await extract_document_events_v1(document_content_text)
    # --- organizations mentioned
    #  TODO: await extract_document_organizations(document_content_text)
    # --- people mentioned + context within document
    #  TODO: await extract_document_people(document_content_text)
    # --- SAVE
    document.status_processing_extractions = "completed"
    session.add(document)
    print('INFO (index_document_docx.py:_index_document_docx_process_extractions): done')


# INDEX_DOCX
async def index_document_docx(session, document_id) -> int:
    print(f"INFO (index_document_docx.py): indexing document #{document_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_document_docx.py): processing document #{document_id} content")
        await _index_document_docx_process_content(session=session, document_id=document_id)
        print(f"INFO (index_document_docx.py): processing document #{document_id} embeddings")
        await _index_document_docx_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_document_docx.py): processing document #{document_id} extractions")
        await _index_document_docx_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_document_docx.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_document_docx.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
