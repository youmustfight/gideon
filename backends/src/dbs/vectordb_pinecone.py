import env
import numpy as np
import pinecone
from sentence_transformers import SentenceTransformer
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from models.gpt import gpt_embedding
from models.clip import clip_text_embedding
from dbs.sa_models import DocumentContent, Embedding
from files.s3_utils import s3_get_file_url, s3_upload_bytes, s3_upload_file
from dbs.vector_utils import write_tensor_to_bytearray, backup_tensor_to_s3

# SETUP
# --- pinecone
pinecone.init(
  api_key=env.env_get_database_pinecone_api_key(),
  environment=env.env_get_database_pinecone_environment()
)
index_documents_clip_url = "documents-clip-8bb34d7.svc.us-west1-gcp.pinecone.io"
index_documents_clip = pinecone.Index("documents-clip")
# TODO: split these into namespaces (https://www.pinecone.io/docs/namespaces/)
# TODO: or actually, instead of namespacing on types of vectors, could do it for prod/dev/local/etc. enviornment names
index_documents_text_url = "documents-text-8bb34d7.svc.us-west1-gcp.pinecone.io"
index_documents_text = pinecone.Index("documents-text")
index_documents_sentences_url = "documents-sentences-8bb34d7.svc.us-west1-gcp.pinecone.io"
index_documents_sentences = pinecone.Index("documents-sentences")


# INDEX UPSERTS

def index_documents_text_add(embedding_id, vector, metadata=None):
    print("INFO (vectordb_pinecone:index_documents_text_add): start", embedding_id)
    pinecone_upsert_record = (str(embedding_id), vector, { "embedding_id": int(embedding_id) })
    # --- append metadata (https://stackoverflow.com/questions/14839528/merge-two-objects-in-python)
    if (metadata != None): pinecone_upsert_record[2].update(metadata)
    # --- index upsert
    index_documents_text.upsert(vectors=[pinecone_upsert_record])
    print("INFO (vectordb_pinecone:index_documents_text_add): upsert", [pinecone_upsert_record[0], pinecone_upsert_record[2]])

def index_documents_sentences_add(embedding_id, vector, metadata=None):
    print("INFO (vectordb_pinecone:index_documents_sentences_add): start", embedding_id)
    pinecone_upsert_record = (str(embedding_id), vector, { "embedding_id": int(embedding_id) })
    # --- append metadata (https://stackoverflow.com/questions/14839528/merge-two-objects-in-python)
    if (metadata != None): pinecone_upsert_record[2].update(metadata)
    # --- index upsert
    index_documents_sentences.upsert(vectors=[pinecone_upsert_record])
    print("INFO (vectordb_pinecone:index_documents_sentences_add): upsert", [pinecone_upsert_record[0], pinecone_upsert_record[2]])

def index_clip_image_add(embedding_id, vector, metadata=None):
    print("INFO (vectordb_pinecone:index_clip_image_add): start", embedding_id)
    pinecone_upsert_record = (str(embedding_id), vector, { "embedding_id": int(embedding_id) })
    # --- append metadata (https://stackoverflow.com/questions/14839528/merge-two-objects-in-python)
    if (metadata != None): pinecone_upsert_record[2].update(metadata)
    # --- index upsert
    index_documents_clip.upsert(vectors=[pinecone_upsert_record])
    print("INFO (vectordb_pinecone:index_clip_image_add): upsert", [pinecone_upsert_record[0], pinecone_upsert_record[2]])


# INDEX QUERIES
  
async def index_documents_text_query(text, top_k=12, score_limit=1.2, score_diff_percent=0.5):
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{text}"')
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    query_results = index_documents_text.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter={ "string_length": { "$gt": 480 } } # ensure min string length so we don't overweight short phrases
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{text}"', matches)
    return matches

def index_documents_sentences_query(text, top_k=12, score_limit=1.2, score_diff_percent=0.5):
    print(f'INFO (vectordb_pinecone:index_documents_sentences_query): query "{text}"')
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    query_results = index_documents_sentences.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter={ "string_length": { "$gt": 80 } } # ensure min string length so we don't overweight short phrases
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None and len(matches) > 0):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_sentences_query): query "{text}"', matches)
    return matches

def index_clip_image_search(image_data):
    pass

def index_clip_text_search(text, top_k=12, score_limit=160, score_diff_percent=0.04):
    print(f'INFO (vectordb_pinecone:index_clip_text_search): query "{text}"')
    text_embedding_tensor = clip_text_embedding(text) # now returns as numpy array
    text_embedding_vector = np.squeeze(text_embedding_tensor).tolist()
    # --- query
    query_results = index_documents_clip.query(
        vector=text_embedding_vector,
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
    )
    # --- rank sort & filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None and len(matches) > 0):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_clip_text_search): query "{text}"', matches)
    return matches

# INDEX VECTOR JOINS

async def get_embeddings_from_search_vectors(session, search_vectors):
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): search_vectors ', search_vectors)
    search_text_embedding_ids = list(map(lambda v: int(v['metadata']['embedding_id']), search_vectors))
    print(f'INFO (vectordb_pinecone.py:get_embeddings_from_search_vectors): search_text_embedding_ids ', search_text_embedding_ids)
    embedding_query = await session.execute(
        sa.select(Embedding)
            .options(
                joinedload(Embedding.document_content).options(
                    joinedload(DocumentContent.document)
                ))
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
