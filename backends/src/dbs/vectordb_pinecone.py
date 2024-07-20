from enum import Enum
from typing import List, Dict, Any

import env
from pinecone import Pinecone, ServerlessSpec
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import DocumentContent, Embedding


# INIT
pc = Pinecone(
    api_key=env.env_get_database_pinecone_api_key(),
    environment="us-east-1")

# INDEXES
class VECTOR_INDEX_ID(Enum):
    index_384_cosine = 'development-384-cosine' # DEPRECATED sentence encoder
    index_768_cosine = env.env_get_database_pinecone_index_768_cosine() # clip (and also will be used by a better sentence encoder)
    index_1024_cosine = 'development-1024-cosine' # DEPRECATED ada 001
    index_1536_cosine = env.env_get_database_pinecone_index_1536_cosine() # ada 002
    index_4096_euclidean = 'development-4096-euclidean' # DEPRECATED curie
    index_12288_euclidean = 'development-12288-euclidean' # DEPRECATED davinci


# CRUD QUERIES
def pinecone_index_query(index: str, namespace: str, vector: List[float], top_k: int, filters: Dict[str, Any] = None):
    print(f'INFO (pinecone_index_query): {index}:{namespace}', filters)
    index = pc.Index(index)
    query_results = index.query(
        vector=vector,
        top_k=top_k,
        namespace=namespace,
        filter=filters,
        include_values=False,
        include_metadata=True
    )
    # Not sure if we should change the shape of this, List[{ id, metadata:{...}, score, values }]
    return query_results.matches

def pinecone_index_upsert(index: str, namespace: str, values: List[Dict[str, Any]]):
    index = pc.Index(index)
    upsert_values = [
        {
            'id': value[0],
            'values': value[1],
            'metadata': value[2],
        }
        for value in values
    ]
    print(f'INFO (pinecone_index_upsert): {index}:{namespace}', [v['id'] for v in upsert_values])
    index.upsert(
        vectors=upsert_values,
        namespace=namespace
    )
    return None

def pinecone_index_delete(index: str, namespace: str, ids: List[str]):
    print(f'INFO (pinecone_index_delete): {index}:{namespace}, ids =', ids)
    index = pc.Index(index)
    index.delete(
        ids=ids,
        namespace=namespace
    )
    return None


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
