import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import Document, DocumentContent, Embedding
from dbs.vectordb_pinecone import get_vector_indexes

async def deindex_document_content(session, document_id):
    '''
    Delete document embeddings + document and remove them from vector databases/indexes
    '''
    # FETCH
    # --- document
    query_document = await session.execute(sa.select(Document).where(Document.id == int(document_id)))
    document = query_document.scalars().first()
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
        print('INFO (deindex_document_content.py) Deleting Embeddings: ', embeddings_ids_strs)
        for index in get_vector_indexes().values():
            print('INFO (deindex_document_content.py) Deleting Embeddings on Index:', index)
            try:
                index.delete(ids=embeddings_ids_strs)
            except Exception as err:
                print('ERROR (deindex_document_content.py) Error:', err)

    # DELETE MODELS/DATA
    # --- embeddings
    await session.execute(sa.delete(Embedding)
        .where(Embedding.id.in_(embeddings_ids_ints)))
    document.status_processing_embeddings = None
    # --- document_content
    await session.execute(sa.delete(DocumentContent)
        .where(DocumentContent.document_id == int(document_id)))
    document.status_processing_content = None
    # --- document properties/extractions
    document.status_processing_extractions = None
    document.document_description = None
    document.document_events = None
    document.document_summary = None
    document.document_summary_one_liner = None
    document.document_citing_slavery_summary = None
    document.document_citing_slavery_summary_one_liner = None

    # SAVE DOCUMENT UPDATES
    session.add(document)
