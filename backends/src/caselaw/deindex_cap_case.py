import pinecone
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import CAPCaseLaw, CAPCaseLawContent, Embedding
from dbs.vectordb_pinecone import pinecone_index_delete

async def deindex_cap_case(session, cap_id):
    '''
    Delete document embeddings + document and remove them from vector databases/indexes
    '''
    print(f'INFO (deindex_cap_case.py) start: {cap_id}')
    # FETCH
    # --- document
    query_cap_case = await session.execute(sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == cap_id))
    cap_case = query_cap_case.scalars().first()
    print(cap_id)
    print(cap_case)
    # --- embeddings (TODO: prob will expand w/ other types of content types)
    query_embeddings = await session.execute(sa.select(Embedding).where(Embedding.cap_case_id == cap_case.id))
    embeddings = query_embeddings.scalars().all()
    embeddings_ids_ints = list(map(lambda e: e.id, embeddings))
    embeddings_ids_strs = list(map(lambda id: str(id), embeddings_ids_ints))
    print('INFO (deindex_cap_case.py) embeddings_ids_ints: ', embeddings_ids_ints)
    print('INFO (deindex_cap_case.py) embeddings_ids_strs: ', embeddings_ids_strs)

    # DELETE INDEX VECTORS (via embedidngs)
    deletes_tuple_dict = {}
    for embedding in embeddings:
        if (deletes_tuple_dict.get((embedding.index_id, embedding.index_partition_id)) == None):
            deletes_tuple_dict[(embedding.index_id, embedding.index_partition_id)] = [str(embedding.id)]
        else:
            deletes_tuple_dict[(embedding.index_id, embedding.index_partition_id)].append(str(embedding.id))

    print('INFO (deindex_cap_case.py) Deleting Embeddings: ', deletes_tuple_dict)
    for delete_tuple in deletes_tuple_dict:
        # pinecone.Index(index_name=delete_tuple[0]).delete(ids=embeddings_ids_strs, namespace=delete_tuple[1])
        pinecone_index_delete(index=delete_tuple[0], namespace=delete_tuple[1], ids=embeddings_ids_strs)

    # DELETE MODELS/DATA
    print('INFO (deindex_cap_case.py) Deleting models')
    # --- embeddings
    await session.execute(sa.delete(Embedding)
        .where(Embedding.id.in_(embeddings_ids_ints)))
    cap_case.status_processing_embeddings = None
    # --- cap_case_content
    await session.execute(sa.delete(CAPCaseLawContent)
        .where(CAPCaseLawContent.cap_case_id == cap_case.id))
    cap_case.status_processing_content = None
    # --- cap_case properties/extractions
    cap_case.status_processing_extractions = None
    cap_case.generated_summary = None
    cap_case.generated_summary_one_liner = None
    cap_case.generated_citing_slavery_summary = None
    cap_case.generated_citing_slavery_summary_one_liner = None

    # SAVE DOCUMENT UPDATES
    session.add(cap_case)
    print(f'INFO (deindex_cap_case.py) done: {cap_id}')
