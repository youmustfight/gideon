import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from agents.ai_action_agent import AI_ACTIONS, create_ai_action_agent
from dbs.sa_models import Document, DocumentContent, Embedding
from indexers.utils.tokenize_string import TOKENIZING_STRATEGY


async def upsert_document_content_vectors(session, document_id):
    print('INFO (upsert_document_content_vectors.py): start')
    # FETCH DATA
    query_document = await session.execute(
        sa.select(Document)
            .options(joinedload(Document.case))
            .where(Document.id == document_id))
    query_embeddings = await session.execute(
        sa.select(Embedding).options(
            joinedload(Embedding.document_content).options(
                joinedload(DocumentContent.document)
        )).where(Embedding.document_content.has(
            DocumentContent.document.has(
                Document.id == int(document_id)))))
    document = query_document.scalars().first()
    embeddings = query_embeddings.scalars().all()
    case = document.case

    # PREP
    # --- indexes (TODO: add an upsert method to agent?)
    aigent_image_embeds = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_image_embed, case_id=case.id)
    aigent_sentence_embeds = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentence_embed, case_id=case.id)
    aigent_sentences_20_embeds = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentences_20_embed, case_id=case.id)
    aigent_max_text_embeds = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_sentences_20_embed, case_id=case.id)
    upserts_image_index = aigent_image_embeds.get_vector_index()
    upserts_sentence_index = aigent_sentence_embeds.get_vector_index()
    upserts_sentences_20_index = aigent_sentences_20_embeds.get_vector_index()
    upserts_max_text_index = aigent_max_text_embeds.get_vector_index()
    # --- upserts
    upserts_image = []
    upserts_sentence = []
    upserts_sentences_20 = []
    upserts_max_text = []
    for embedding in embeddings:
        em = embedding
        dc = embedding.document_content
        # --- setup metadata
        metadata = {
            "case_id": case.id,
            "case_uuid": str(case.uuid),
            "document_id": document_id,
            "document_content_id": dc.id,
            "embedding_id": int(em.id)
        }
        if (dc.text != None): metadata['string_length'] = len(dc.text)
        # --- setup record
        upsert_record = (str(em.id), em.vector_json, metadata)
        print('INFO (upsert_document_content_vectors.py): upsert_record', (str(em.id), len(em.vector_json), metadata))
        # --- index content (sentence)
        if (dc.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value):
            upserts_sentence.append(upsert_record)
        # --- index content (sentences 20)
        if (dc.tokenizing_strategy == TOKENIZING_STRATEGY.sentences_20.value):
            upserts_sentences_20.append(upsert_record)
        # --- index content (max_size)
        if (dc.tokenizing_strategy == TOKENIZING_STRATEGY.max_size.value):
            upserts_max_text.append(upsert_record)
        # --- index content (image)
        if (dc.image_file_id != None):
            upserts_image.append(upsert_record)

    # UPSERT TO INDEXES
    # --- sentence
    if (upserts_sentence_index != None and len(upserts_sentence) > 0):
        print('INFO (upsert_document_content_vectors.py): upserts_sentence_index', len(upserts_sentence))
        upserts_sentence_index.upsert(upserts_sentence)
    # --- sentences 20
    if (upserts_sentences_20_index != None and len(upserts_sentences_20) > 0):
        print('INFO (upsert_document_content_vectors.py): upserts_sentences_20_index', len(upserts_sentences_20))
        upserts_sentences_20_index.upsert(upserts_sentences_20)
    # --- max text
    if (upserts_max_text_index != None and len(upserts_max_text) > 0):
        print('INFO (upsert_document_content_vectors.py): upserts_max_text_index', len(upserts_max_text))
        upserts_max_text_index.upsert(upserts_max_text)
    # --- image
    if (upserts_image_index != None and len(upserts_image) > 0):
        print('INFO (upsert_document_content_vectors.py): upserts_image_index', len(upserts_image))
        upserts_image_index.upsert(upserts_image)
