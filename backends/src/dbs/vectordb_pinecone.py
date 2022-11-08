import env
import numpy as np
import pinecone
import random
from sentence_transformers import SentenceTransformer
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
import uuid

from models.gpt import gpt_embedding, gpt_vars
from dbs.sa_models import DocumentContent, Embedding
from s3_utils import s3_get_file_url, s3_upload_bytes, s3_upload_file
from dbs.vector_utils import write_tensor_to_bytearray, backup_tensor_to_s3

# SETUP
# --- models
clip_model = SentenceTransformer('clip-ViT-B-32')
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


# TODO
def index_clip_add_image(image_filepaths, filename):
  pass

# TODO
def index_clip_search_images_by_text(text_query):
  pass

async def index_documents_text_add(session, text, document_id=None, document_content_id=None):
    print("INFO (vectordb_pinecone:index_documents_text_add): start")
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- save embedding (we're doing an execute() + insert() so we can retrieve an id, not possible with add())
    print("INFO (vectordb_pinecone:index_documents_text_add): save embedding")
    embedding_query = await session.execute(
        sa.insert(Embedding).values(
            document_id=document_id,
            document_content_id=document_content_id,
            encoded_model="gpt3",
            encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
            encoding_strategy="text",
            text=text,
        ).returning(Embedding.id)
    )
    embedding_id = embedding_query.scalar_one_or_none() # grabs the returned id integer
    # --- save as .npy file to s3 as backup
    backup_tensor_to_s3(embedding_id, text_embedding_tensor)
    # --- add to index (single item indexing means 1, dimensions?)
    # id, values, metadata
    pinecone_upsert_record = (
        str(embedding_id),
        np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
        { "embedding_id": int(embedding_id) },
    )
     # None/null values throw 400s, so need to build up meta data. Ex: "document_id": None, "document_content_id": None,
    if (document_id != None):
        pinecone_upsert_record[2]["document_id"] = document_id
    if (document_content_id != None):
        pinecone_upsert_record[2]["document_content_id"] = document_content_id
    print("INFO (vectordb_pinecone:index_documents_text_add): upsert vector", [pinecone_upsert_record[0], pinecone_upsert_record[2]])
    index_documents_text.upsert(vectors=[pinecone_upsert_record])

async def index_documents_sentences_add(session, text, document_id=None, document_content_id=None):
    print("INFO (vectordb_pinecone:index_documents_sentences_add): start")
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- save embedding (we're doing an execute() + insert() so we can retrieve an id, not possible with add())
    print("INFO (vectordb_pinecone:index_documents_sentences_add): save embedding")
    embedding_query = await session.execute(
        sa.insert(Embedding).values(
            document_id=document_id,
            document_content_id=document_content_id,
            encoded_model="gpt3",
            encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
            encoding_strategy="text",
            text=text,
        ).returning(Embedding.id)
    )
    embedding_id = embedding_query.scalar_one_or_none() # grabs the returned id integer
    # --- save as .npy file to s3 as backup
    backup_tensor_to_s3(embedding_id, text_embedding_tensor)
    # --- add to index (single item indexing means 1, dimensions?)
    pinecone_upsert_record = (
        str(embedding_id),
        np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
        { "embedding_id": int(embedding_id) },
    )
    # None/null values throw 400s, so need to build up meta data. Ex: "document_id": None, "document_content_id": None,
    if (document_id != None):
        pinecone_upsert_record[2]["document_id"] = document_id
    if (document_content_id != None):
        pinecone_upsert_record[2]["document_content_id"] = document_content_id
    print("INFO (vectordb_pinecone:index_documents_sentences_add): upsert vector", [pinecone_upsert_record[0], pinecone_upsert_record[2]])
    index_documents_sentences.upsert(vectors=[pinecone_upsert_record])
  

async def index_documents_text_query(text, top_k=10, score_limit=1.2, score_diff_percent=0.3):
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{text}"')
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- query index TODO: filter on metadata
    query_results = index_documents_text.query(
        vector=np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter={ "embedding_id": { "$gt": 234 } } # HACK: just filtering out all prior fails
        # TODO: namespace=""
    )
    # --- filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{text}"', matches)
    return matches

def index_documents_sentences_query(text, top_k=10, score_limit=1.2, score_diff_percent=0.3):
    print(f'INFO (vectordb_pinecone:index_documents_sentences_query): query "{text}"')
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- query index TODO: filter on metadata
    query_results = index_documents_sentences.query(
        vector=np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
        top_k=top_k,
        include_values=False,
        includeMetadata=True,
        filter={ "embedding_id": { "$gt": 234 } } # HACK: just filtering out all prior fails
        # TODO: namespace=""
    )
    # --- filters
    matches = query_results['matches']
    if (score_limit != None):
        matches = list(filter(lambda m: m['score'] < score_limit, matches))
    if (score_diff_percent != None):
        lowest_score = matches[0].score
        matches = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_diff_percent)), matches))
    print(f'INFO (vectordb_pinecone:index_documents_text_query): query "{text}"', matches)
    return matches

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
