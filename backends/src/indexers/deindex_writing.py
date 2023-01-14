import pinecone
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import Writing, Embedding
from dbs.vectordb_pinecone import pinecone_index_delete

async def deindex_writing(session, writing_id):
    '''
    Delete writing embeddings + writing and remove them from vector databases/indexes
    '''
    # FETCH
    # --- writing
    query_writing = await session.execute(sa.select(Writing).where(Writing.id == int(writing_id)))
    writing = query_writing.scalars().first()
    # --- embeddings
    query_embeddings = await session.execute(
        sa.select(Embedding)
          .where(Embedding.writing_id == int(writing_id)))
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

    print('INFO (deindex_writing.py) Deleting Embeddings: ', deletes_tuple_dict)
    for delete_tuple in deletes_tuple_dict:
        # pinecone.Index(index_name=delete_tuple[0]).delete(ids=embeddings_ids_strs, namespace=delete_tuple[1])
        pinecone_index_delete(index=delete_tuple[0], namespace=delete_tuple[1], ids=embeddings_ids_strs)

    # DELETE MODELS/DATA
    # --- embeddings
    await session.execute(sa.delete(Embedding)
        .where(Embedding.id.in_(embeddings_ids_ints)))

    # SAVE DOCUMENT UPDATES
    session.add(writing)
