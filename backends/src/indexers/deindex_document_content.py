import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import Document, DocumentContent, Embedding
from dbs.vectordb_pinecone import get_vector_indexes

async def deindex_document_content(session, document_id):
    '''
    Delete document embeddings + document and remove them from vector databases/indexes
    '''
    # FETCH
    # --- embeddings
    query_embeddings = await session.execute(
        sa.select(Embedding).options(
            joinedload(Embedding.document_content).options(
                joinedload(DocumentContent.document)
        )).where(Embedding.document_content.has(
            DocumentContent.document.has(
                Document.id == int(document_id)))))
    embeddings = query_embeddings.scalars().all()
    embeddings_ids_ints = list(map(lambda e: e.id, embeddings))
    embeddings_ids_strs = list(map(lambda id: str(id), embeddings_ids_ints))

    # DELETE INDEX VECTORS (via embedidngs)
    if (len(embeddings_ids_strs) > 0):
        print('INFO Deleting Embeddings: ', embeddings_ids_strs)
        for index in get_vector_indexes().values():
            print('INFO Deleting Embeddings on Index:', index)
            index.delete(ids=embeddings_ids_strs)

    # DELETE MODELS
    # --- embeddings
    await session.execute(sa.delete(Embedding)
        .where(Embedding.id.in_(embeddings_ids_ints)))
    # --- document_content
    await session.execute(sa.delete(DocumentContent)
        .where(DocumentContent.document_id == int(document_id)))
