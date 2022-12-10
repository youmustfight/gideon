from enum import Enum
import env
import pinecone
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from dbs.sa_models import DocumentContent, Embedding

# INDEXES
pinecone.init(
  api_key=env.env_get_database_pinecone_api_key(),
  environment=env.env_get_database_pinecone_environment()
)
class VECTOR_INDEX_ID(Enum):
    documents_clip_768 = 'documents-clip-768'
    documents_text_384 = 'documents-text-384'
    documents_text_1024 = 'documents-text-1024'
    documents_text_4096 = 'documents-text-4096'
    documents_text_12288 = 'documents-text-12288'


# HELPERS
# --- index fetching
def get_vector_indexes():
    return {
        VECTOR_INDEX_ID.documents_clip_768.value: pinecone.Index(index_name=VECTOR_INDEX_ID.documents_clip_768.value), # cosine
        VECTOR_INDEX_ID.documents_text_384.value: pinecone.Index(index_name=VECTOR_INDEX_ID.documents_text_384.value), # cosine (prev euclidian bc higher dimensionality)
        VECTOR_INDEX_ID.documents_text_1024.value: pinecone.Index(index_name=VECTOR_INDEX_ID.documents_text_1024.value), # cosine (prev euclidian bc higher dimensionality)
        VECTOR_INDEX_ID.documents_text_4096.value: pinecone.Index(index_name=VECTOR_INDEX_ID.documents_text_4096.value), # euclidan bc higher dimensionality
        VECTOR_INDEX_ID.documents_text_12288.value: pinecone.Index(index_name=VECTOR_INDEX_ID.documents_text_12288.value), # euclidan bc higher dimensionality
    }

# --- search vectors 2 embedding models
async def get_embeddings_from_search_vectors(session, search_vectors):
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): search_vectors ', search_vectors)
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
