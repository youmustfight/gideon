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
    index_384_cosine = 'development-384-cosine' # sentence encoder
    index_768_cosine = env.env_get_database_pinecone_index_768_cosine() # clip (and also will be used by a better sentence encoder)
    index_1024_cosine = 'development-1024-cosine' # DEPRECATED ada 001
    index_1536_cosine = env.env_get_database_pinecone_index_1536_cosine() # ada 002
    index_4096_euclidean = 'development-4096-euclidean' # DEPRECATED curie
    index_12288_euclidean = 'development-12288-euclidean' # DEPRECATED davinci


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
