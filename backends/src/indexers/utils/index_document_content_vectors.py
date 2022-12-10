import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from aia.agent import AI_ACTIONS, create_ai_action_agent
from dbs.sa_models import Document, DocumentContent, Embedding


async def index_document_content_vectors(session, document_id):
    print('INFO (index_document_content_vectors.py): start')
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
    aigent_max_text_embeds = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_text_max_size_embed, case_id=case.id)
    upserts_image_index = aigent_image_embeds.get_vector_index()
    upserts_sentences_index = aigent_sentence_embeds.get_vector_index()
    upserts_max_text_index = aigent_max_text_embeds.get_vector_index()
    # --- upserts
    upserts_image = []
    upserts_sentences = []
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
        print('INFO (index_document_content_vectors.py): upsert_record', (str(em.id), len(em.vector_json), metadata))
        # --- index content (sentence)
        if (dc.tokenizing_strategy == "sentence"):
            upserts_sentences.append(upsert_record)
        # --- index content (max_size)
        if (dc.tokenizing_strategy == "max_size"):
            upserts_max_text.append(upsert_record)
        # --- index content (image)
        if (dc.image_file_id != None):
            upserts_image.append(upsert_record)

    # UPSERT TO INDEXES
    if (upserts_image_index != None and len(upserts_image) > 0):
        print('INFO (index_document_content_vectors.py): upserts_image_index', len(upserts_image))
        upserts_image_index.upsert(upserts_image)
    if (upserts_sentences_index != None and len(upserts_sentences) > 0):
        print('INFO (index_document_content_vectors.py): upserts_sentences_index', len(upserts_sentences))
        upserts_sentences_index.upsert(upserts_sentences)
    if (upserts_max_text_index != None and len(upserts_max_text) > 0):
        print('INFO (index_document_content_vectors.py): upserts_max_text_index', len(upserts_max_text))
        upserts_max_text_index.upsert(upserts_max_text)
