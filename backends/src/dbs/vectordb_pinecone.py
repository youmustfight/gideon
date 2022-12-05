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
pinecone_index_documents_clip_768 = pinecone.Index("documents-clip-768") # cosine
pinecone_index_documents_text_384 = pinecone.Index("documents-text-384") # cosine (prev euclidian bc higher dimensionality)
pinecone_index_documents_text_1024 = pinecone.Index("documents-text-1024") # cosine (prev euclidian bc higher dimensionality)
pinecone_index_documents_text_4096 = pinecone.Index("documents-text-4096") # euclidan bc higher dimensionality
pinecone_index_documents_text_12288 = pinecone.Index("documents-text-12288") # euclidan bc higher dimensionality


# HELPERS
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
