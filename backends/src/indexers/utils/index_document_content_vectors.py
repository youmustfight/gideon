import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.vectordb_pinecone import pinecone_index_documents_text_384, pinecone_index_documents_text_1024, pinecone_index_documents_clip
from dbs.sa_models import Document, DocumentContent, Embedding


# HELPERS
# --- sentences
def upsert_text_384(vectors):
    print(f'INFO (index_documents_text_sentence): upseting {len(vectors)} vectors')
    if len(vectors) > 0:
        pinecone_index_documents_text_384.upsert(vectors=vectors)
# --- breadth/context
def upsert_text_1024(vectors):
    print(f'INFO (index_documents_text_sentence): upseting {len(vectors)} vectors')
    if len(vectors) > 0:
        pinecone_index_documents_text_1024.upsert(vectors=vectors)
# --- images multi-modal
def upsert_clip(vectors):
    print(f'INFO (index_documents_image): upseting {len(vectors)} vectors')
    if len(vectors) > 0:
        pinecone_index_documents_clip.upsert(vectors=vectors)


# RUNNER
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
    upserts_text_384 = []
    upserts_text_1024 = []
    upserts_clip = []
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
        # --- setup record
        upsert_record = (str(em.id), em.vector_json, { "embedding_id": int(em.id) }.update(metadata))
        # --- index content (sentence)
        if (dc.tokenizing_strategy == "sentence"):
            upserts_text_384.append(upsert_record)
        # --- index content (max_size)
        if (dc.tokenizing_strategy == "max_size"):
            upserts_text_1024.append(upsert_record)
        # --- index content (image)
        if (dc.image_file_id != None):
            upserts_clip.append(upsert_record)

    # INDEX
    upsert_text_384(upserts_text_384)
    upsert_text_1024(upserts_text_1024)
    upsert_clip(upserts_clip)
