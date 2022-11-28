import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.vectordb_pinecone import index_documents_sentences_add, index_documents_text_add, index_clip_image_add
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

    # INDEX
    for embedding in embeddings:
        em = embedding
        dc = embedding.document_content
        # --- setup metadata
        metadata = {
            "case_id": document.case_id,
            "case_uuid": str(case.uuid),
            "document_id": document_id,
            "document_content_id": dc.id,
        }
        if (dc.text != None): metadata.update({ 'string_length': len(dc.text) })
        # --- index content (max_size)
        if (dc.tokenizing_strategy == "max_size"):
            index_documents_text_add(
                embedding_id=em.id,
                vector=em.vector_json,
                metadata=metadata)
        # --- index content (sentence)
        if (dc.tokenizing_strategy == "sentence"):
            index_documents_sentences_add(
                embedding_id=em.id,
                vector=em.vector_json,
                metadata=metadata)
        # --- index content (image)
        if (dc.image_file_id != None):
            index_clip_image_add(
                embedding_id=em.id,
                vector=em.vector_json,
                metadata=metadata)
