import pinecone
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import Document, DocumentContent, Embedding

async def deindex_document(session, document_id):
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
    deletes_tuple_dict = {}
    for embedding in embeddings:
        if (deletes_tuple_dict.get((embedding.index_id, embedding.index_partition_id)) == None):
            deletes_tuple_dict[(embedding.index_id, embedding.index_partition_id)] = [str(embedding.id)]
        else:
            deletes_tuple_dict[(embedding.index_id, embedding.index_partition_id)].append(str(embedding.id))

    print('INFO (deindex_document.py) Deleting Embeddings: ', deletes_tuple_dict)
    for delete_tuple in deletes_tuple_dict:
        pinecone.Index(index_name=delete_tuple[0]).delete(ids=embeddings_ids_strs, namespace=delete_tuple[1])

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

    # SAVE DOCUMENT UPDATES
    session.add(document)
