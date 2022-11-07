import env
import numpy as np
import pinecone
import random
from sentence_transformers import SentenceTransformer
from sqlalchemy import insert
import uuid

from gideon_gpt import gpt_embedding, gpt_vars
from models import Document, DocumentContent, Embedding, File
from s3_utils import s3_get_file_url, s3_upload_bytes, s3_upload_file
from vector_dbs.vector_utils import write_tensor_to_bytearray

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
  uuidv4 = str(uuid.uuid4())
  # --- get embedding
  text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
  # --- save as .npy file to s3 as backup
  numpy_tensor_bytearray = write_tensor_to_bytearray(text_embedding_tensor)
  npy_file_key = f"index_documents_{uuidv4}.npy"
  s3_upload_bytes(npy_file_key, numpy_tensor_bytearray)
  # --- save embedding (we're doing an execute() + insert() so we can retrieve an id, not possible with add())
  print("INFO (vectordb_pinecone:index_documents_text_add): save embedding")
  embedding_query = await session.execute(
      insert(Embedding).values(
          document_id=document_id,
          document_content_id=document_content_id,
          encoded_model="gpt3",
          encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
          encoding_strategy="text",
          text=text,
          npy_url=s3_get_file_url(npy_file_key)
      ).returning(Embedding.id)
  )
  embedding_id = embedding_query.scalar_one_or_none() # grabs the returned id integer
  # --- add to index (single item indexing means 1, dimensions?)
  # id, values, metadata
  pinecone_upsert_record = (
    str(embedding_id),
    np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
    { "embedding_id": embedding_id }, # TODO: None/null values throw 400s, so need to build up meta data. Ex: "document_id": None, "document_content_id": None,
  )
  print("INFO (vectordb_pinecone:index_documents_text_add): upsert vector", pinecone_upsert_record)
  index_documents_text.upsert(vectors=[pinecone_upsert_record])

async def index_documents_text_query(text):
  # --- get embedding
  text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
  # --- query index TODO: filter on metadata
  query_results = index_documents_text.query(
    vector=np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
    top_k=10,
    include_values=True
  )
  # --- return matches
  return query_results['matches']

async def index_documents_sentences_add(session, text, document_id=None, document_content_id=None):
  print("INFO (vectordb_pinecone:index_documents_sentences_add): start")
  uuidv4 = str(uuid.uuid4())
  # --- get embedding
  text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
  # --- save as .npy file to s3 as backup
  numpy_tensor_bytearray = write_tensor_to_bytearray(text_embedding_tensor)
  npy_file_key = f"index_documents_{uuidv4}.npy"
  s3_upload_bytes(npy_file_key, numpy_tensor_bytearray)
  # --- save embedding (we're doing an execute() + insert() so we can retrieve an id, not possible with add())
  print("INFO (vectordb_pinecone:index_documents_sentences_add): save embedding")
  embedding_query = await session.execute(
      insert(Embedding).values(
          document_id=document_id,
          document_content_id=document_content_id,
          encoded_model="gpt3",
          encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
          encoding_strategy="text",
          text=text,
          npy_url=s3_get_file_url(npy_file_key)
      ).returning(Embedding.id)
  )
  embedding_id = embedding_query.scalar_one_or_none() # grabs the returned id integer
  # --- add to index (single item indexing means 1, dimensions?)
  # id, values, metadata
  pinecone_upsert_record = (
    str(embedding_id),
    np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
    { "embedding_id": embedding_id }, # TODO: None/null values throw 400s, so need to build up meta data. Ex: "document_id": None, "document_content_id": None,
  )
  print("INFO (vectordb_pinecone:index_documents_sentences_add): upsert vector", pinecone_upsert_record)
  index_documents_sentences.upsert(vectors=[pinecone_upsert_record])
  
async def index_documents_sentences_query(text):
  # --- get embedding
  text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
  # --- query index TODO: filter on metadata
  query_results = index_documents_sentences.query(
    vector=np.squeeze(text_embedding_tensor).tolist(), # needed for serialization
    top_k=10,
    include_values=True
  )
  # --- return matches
  return query_results['matches']