import env
import numpy as np
import pinecone
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from models.gpt import gpt_embedding
from models.clip import clip_text_embedding
from dbs.sa_models import DocumentContent, Embedding

# SETUP
# --- pinecone
pinecone.init(
  api_key=env.env_get_database_pinecone_api_key(),
  environment=env.env_get_database_pinecone_environment()
)
pinecone_index_documents_clip = pinecone.Index("documents-clip-768") # cosine
pinecone_index_documents_text_384 = pinecone.Index("documents-text-384") # cosine (prev euclidian bc higher dimensionality)
pinecone_index_documents_text_1024 = pinecone.Index("documents-text-1024") # cosine (prev euclidian bc higher dimensionality)

# INDEX QUERIES

async def index_documents_text_query(query_text, case_uuid, top_k=12, score_limit=1.2, score_diff_percent=0.15):
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{query_text}"')
    text_embedding_tensor = gpt_embedding(query_text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    # USES EUCLIDIAN SO LOWER SCORE IS BETTER MATCH?????????
    query_filter = { "string_length": { "$gt": 480 } }
    if (case_uuid != None):
        query_filter.update({ "case_uuid": { "$eq": str(case_uuid) } })
    query_results = pinecone_index_documents_text_1024.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter=query_filter # ensure min string length so we don't overweight short phrases
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{query_text}"', matches)
    return matches

def index_documents_sentences_query(query_text, case_uuid, top_k=12, score_limit=1.2, score_diff_percent=0.2):
    print(f'INFO (vectordb_pinecone:index_documents_sentences_query): query "{query_text}"')
    text_embedding_tensor = gpt_embedding(query_text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    # USES EUCLIDIAN SO LOWER SCORE IS BETTER MATCH?????????
    query_filter = { "string_length": { "$gt": 80 } }
    if (case_uuid != None):
        query_filter.update({ "case_uuid": { "$eq": str(case_uuid) } })
    query_results = pinecone_index_documents_text_384.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter=query_filter # ensure min string length so we don't overweight short phrases
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None and len(matches) > 0):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_sentences_query): query "{query_text}"', matches)
    return matches

def index_clip_image_search(image_data):
    pass

def index_clip_text_search(query_text, case_uuid, top_k=12, score_limit=0.1, score_diff_percent=0.1):
    print(f'INFO (vectordb_pinecone:index_clip_text_search): query "{query_text}"')
    text_embedding_tensor = clip_text_embedding(query_text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    # USES COSINE SO HIGHER SCORE IS BETTER MATCH?????????
    query_filter = {}
    if (case_uuid != None):
        query_filter.update({ "case_uuid": { "$eq": str(case_uuid) } })
    query_results = pinecone_index_documents_clip.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter=query_filter
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] > score_limit, matches))
    if (score_diff_percent != None and len(matches) > 0):
        highest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] > (highest_score - (highest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_clip_text_search): query "{query_text}"', matches)
    return matches


# INDEX VECTOR JOINS

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

async def get_document_content_from_search_vectors(session, search_vectors):
    print(f'INFO (vectordb_pinecone.py:get_document_content_from_search_vectors): search_vectors ', search_vectors)
    embeddings = await get_embeddings_from_search_vectors(session, search_vectors)
    document_content = list(map(lambda e: e.document_content, embeddings))
    print(f'INFO (vectordb_pinecone.py:get_document_content_from_search_vectors): document_content ', document_content)
    return document_content
