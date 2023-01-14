from enum import Enum
from typing import List

import requests
import env
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import DocumentContent, Embedding

# INDEXES
class VECTOR_INDEX_ID(Enum):
    index_384_cosine = 'development-384-cosine' # DEPRECATED sentence encoder
    index_768_cosine = env.env_get_database_pinecone_index_768_cosine() # clip (and also will be used by a better sentence encoder)
    index_1024_cosine = 'development-1024-cosine' # DEPRECATED ada 001
    index_1536_cosine = env.env_get_database_pinecone_index_1536_cosine() # ada 002
    index_4096_euclidean = 'development-4096-euclidean' # DEPRECATED curie
    index_12288_euclidean = 'development-12288-euclidean' # DEPRECATED davinci


# CRUD QUERIES
# DEPRECATED: can't use the python library because it's causing SSL issues ffs
    # def _get_vector_index(self):
    #     return pinecone.Index(self.index_id)
# def _get_vector_index(self):
    #     return pinecone.Index(self.index_id)
def _get_pinecone_index_url(vector_index_id: str):
    if vector_index_id == VECTOR_INDEX_ID.index_768_cosine.value:
        return env.env_get_database_pinecone_index_768_cosine_url()
    if vector_index_id == VECTOR_INDEX_ID.index_1536_cosine.value:
        return env.env_get_database_pinecone_index_1536_cosine_url()
    raise 'Unable to get index URL'
# DEPRECATED: can't use the python library because it's causing SSL issues ffs
# query_results = self._get_vector_index().query(
#     namespace=self.index_partition_id,
#     vector=vector,
#     top_k=top_k,
#     include_values=False,
#     includeMetadata=True,
#     filter=filters)
def pinecone_index_query(index: str, namespace: str, vector: List[float], top_k: int, filters=None):
    print(f'INFO (pinecone_index_query): {index}:{namespace}')
    query_results = requests.post(
        f'{_get_pinecone_index_url(index)}/query',
        json={
            'namespace': namespace,
            'topK': top_k,
            'filter': filters,
            'includeValues': False,
            'includeMetadata': True,
            'vector': vector
        },
        headers={
            'Accept': 'application/json',
            'Api-Key': env.env_get_database_pinecone_api_key(),
            'Content-Type': 'application/json'
        }
    )
    # get json payload
    query_results = query_results.json()
    # convert matches to dicts to be consistent w/ pinecone query lib
    query_result_matches = list(map(lambda m: dict(m), query_results['matches']))
    # return
    return query_result_matches
# DEPRECATED: can't use the python library because it's causing SSL issues ffs
# pinecone.Index(index_name=index_tuple[0]).upsert(
#     vectors=upserts_tuple_dict[index_tuple],
#     namespace=index_tuple[1])
def pinecone_index_upsert(index: str, namespace: str, values):
    print(f'INFO (pinecone_index_upsert): {index}:{namespace}')
    # TODO: syntax follows pinecone lib but it's a little jank feeling
    for value in values:
        upsert_value = {
            'id': value[0],
            'values': value[1],
            'metadata': value[2],
        }
        requests.post(
            f'{_get_pinecone_index_url(index)}/vectors/upsert',
            json={
                'namespace': namespace,
                'values': [upsert_value]
            },
            headers={
                'Accept': 'application/json',
                'Api-Key': env.env_get_database_pinecone_api_key(),
                'Content-Type': 'application/json'
            }
        )
    return None
# DEPRECATED: can't use the python library because it's causing SSL issues ffs
# pinecone.Index(index_name=delete_tuple[0]).delete(ids=embeddings_ids_strs, namespace=delete_tuple[1])
def pinecone_index_delete(index: str, namespace: str, ids: List[str]):
    print(f'INFO (pinecone_index_delete): {index}:{namespace}, ids =', ids)
    requests.post(
        f'{_get_pinecone_index_url(index)}/vectors/delete',
        json={
            'namespace': namespace,
            'ids': ids
        },
        headers={
            'Accept': 'application/json',
            'Api-Key': env.env_get_database_pinecone_api_key(),
            'Content-Type': 'application/json'
        }
    )


# HELPERS
# --- search vectors 2 embedding models
async def get_embeddings_from_search_vectors(session, search_vectors):
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): search_vectors ', search_vectors)
    # we upsert search vectors w/ database embedding.id as the pinecone vector db
    search_text_embedding_ids = list(map(lambda v: int(v['metadata']['embedding_id']), search_vectors))
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): search_text_embedding_ids ', search_text_embedding_ids)
    embedding_query = await session.execute(
        sa.select(Embedding)
            .options(
                joinedload(Embedding.document_content)
                    .options(
                        joinedload(DocumentContent.document),
                        joinedload(DocumentContent.image_file),
                    )
            )
            .where(Embedding.id.in_(search_text_embedding_ids))
    )
    embeddings = embedding_query.scalars().all()
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): embeddings ', embeddings)
    return embeddings

# --- search vectors 2 document content models
async def get_document_content_from_search_vectors(session, search_vectors):
    print(f'INFO (vectordb_pinecone.py:get_document_content_from_search_vectors): search_vectors ', search_vectors)
    embeddings = await get_embeddings_from_search_vectors(session, search_vectors)
    document_content = list(map(lambda e: e.document_content, embeddings))
    print(f'INFO (vectordb_pinecone.py:get_document_content_from_search_vectors): document_content ', document_content)
    return document_content
