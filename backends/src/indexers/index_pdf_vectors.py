import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.vectordb_pinecone import index_documents_sentences_add, index_documents_text_add
from dbs.sa_models import Document, DocumentContent, Embedding

async def index_pdf_vectors(session, document_id):
    # FETCH
    query_embeddings = await session.execute(
        sa.select(Embedding).options(
            joinedload(Embedding.document_content).options(
                joinedload(DocumentContent.document)
        )).where(Embedding.document_content.has(
            DocumentContent.document.has(
                Document.id == int(document_id)))))
    embeddings = query_embeddings.scalars().all()
    # INDEX
    for embedding in embeddings:
        em = embedding
        dc = embedding.document_content
        # --- index content (max_size)
        if (dc.tokenizing_strategy == "max_size"):
            index_documents_text_add(
                embedding_id=em.id,
                vector=em.vector_json,
                metadata={
                    "document_id": document_id,
                    "document_content_id": dc.id,
                    "string_length": len(dc.text)
                })
        # --- index content (sentence)
        if (dc.tokenizing_strategy == "sentence"):
            index_documents_sentences_add(
                embedding_id=em.id,
                vector=em.vector_json,
                metadata={
                    "document_id": document_id,
                    "document_content_id": dc.id,
                    "string_length": len(dc.text)
                })
