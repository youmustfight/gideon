import faiss
import io
import numpy
import os
import pickle
import random
from sentence_transformers import SentenceTransformer
from sqlalchemy import insert
import uuid

from models.gpt import gpt_embedding, gpt_vars
from files.file_utils import get_file_path
from dbs.sa_models import Document, DocumentContent, Embedding, File
from files.s3_utils import s3_get_file_url, s3_upload_file_bytes, s3_upload_file
from dbs.vector_utils import write_tensor_to_bytearray

# FFS FIGURING THIS OUT STILL
# https://anttihavanko.medium.com/building-image-search-with-openai-clip-5a1deaa7a6e2
# https://github.com/criteo/autofaiss
# https://stackoverflow.com/questions/47272971/pytorch-how-to-convert-data-into-tensor
# https://github.com/facebookresearch/faiss/
# https://github.com/facebookresearch/faiss/wiki/The-index-factory
# https://github.com/facebookresearch/faiss/wiki/Faiss-indexes
# https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing
# --- IDMap,Flat attempt:
# https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index#then-flat
# https://github.com/facebookresearch/faiss/issues/1118
# https://stackoverflow.com/questions/67956633/typeerror-in-method-indexidmap-add-with-ids-argument-4-of-type-faissindex


index_clip = None
index_clip_model = SentenceTransformer('clip-ViT-B-32') # TODO: use @336 variant of L/14. doing this for now bc less memory usage? (SentenceTransformer('clip-ViT-L-14'))
index_clip_save_path = get_file_path("../indexed/faiss/clip.index")
index_documents = None
index_documents_save_path = get_file_path("../indexed/faiss/documents.index")
index_sentences = None
index_sentences_save_path = get_file_path("../indexed/faiss/sentences.index")

# INDEX OPS
# --- build
def build_index(index_save_path):
    print(f"INFO (vectordb_faiss.build_index): Building... {index_save_path}")
    built_index = None
    # IF INDEX SAVED
    if os.path.isfile(index_save_path):
        built_index = faiss.read_index(index_save_path)
    # IF NOT, BUILD
    else:
        dimensions = None
        # CLIP
        if index_save_path == index_clip_save_path:
            # --- get future tensor dimensions for index params
            image_index_embedding_sample = index_clip_model.encode([get_file_path("../documents/gideon.png")])
            print("INFO (vectordb_faiss.build_index): shape =", image_index_embedding_sample.shape)
            # --- build index
            # IVF_VORONI_CLUSTERS = 39 # only needed if we're doing ann styled indexes
            dimensions = image_index_embedding_sample.shape[1] # (1, 224)
            print("INFO (vectordb_faiss.build_index): dimensions =", dimensions)
            # FYI: If we're using an inverted index like IFV, we have to train i think to rebuild the top level indexes, otherwise it's trained
            # FYI: Only IVF indexes allow add_with_ids, L2 does not. Flat is a storage type. 
            # FYI: Not using a IVF index first means, means we're doing "exchaustive" search which may be better anyways for the legal domain since it's not excluding any result
            # FYI: IDMap + Flat means we can get knn exhaustive search w/ add_with_ids 
            built_index = faiss.index_factory(dimensions, "IDMap,Flat") # "Flat" "IVF4096,Flat" f"IVF{DIMENSIONS},Flat" f"IVF{IVF_VORONI_CLUSTERS},Flat"
        # GPT3
        if index_save_path == index_documents_save_path or index_save_path == index_sentences_save_path:
            # --- get future tensor dimensions for index params
            text_index_embedding_sample = gpt_embedding("example")
            print("INFO (vectordb_faiss.build_index): shape =", text_index_embedding_sample.shape)
            # --- build index
            dimensions = text_index_embedding_sample.shape[0] # only 1 shape data point to reference, unlike clip encode which returns 2 data points on top axis
            print("INFO (vectordb_faiss.build_index): dimensions =", dimensions)
            built_index = faiss.index_factory(dimensions, "IDMap,Flat")
    # RETURN (print some info to check)
    print("INFO (vectordb_faiss.build_index): is_trained", built_index.is_trained)
    print("INFO (vectordb_faiss.build_index): ntotal", built_index.ntotal)
    return built_index
# --- save
def save_index(index, index_save_path):
    print(f"INFO (vectordb_faiss.save_index): saving '{index_save_path}'")
    faiss.write_index(index, index_save_path)
def save_indexes():
    print("INFO (vectordb_faiss.save_indexes): saving")
    save_index(index_clip, index_clip_save_path)
    save_index(index_documents, index_documents_save_path)
    save_index(index_sentences, index_sentences_save_path)

# BUILD INDEXES
# --- clip
index_clip = build_index(index_clip_save_path)
# --- documents + sentences
index_documents = build_index(index_documents_save_path)
index_sentences = build_index(index_sentences_save_path)
# SAVE INDEXES
# save_indexes()

# INDEX QUERY
# --- clip
def index_clip_add_image(image_filepaths, filename):
    print(f"INFO (vectordb_faiss.clip_add_image): '{filename}'")
    image_embedding = index_clip_model.encode(image_filepaths) # returns numpy array w/ shape of (x inserted, params)
    print(f"INFO (vectordb_faiss.clip_add_image): shape", image_embedding.shape)
    # FYI: we have to treat ids as a numpy.array() bc code within checks for shape property, not array length
    # https://github.com/facebookresearch/faiss/blob/c5b49b79df57cab7b7890c28f0ee5cb7329cbddd/faiss/python/class_wrappers.py#L621
    # TODO: connect w/ database ids
    ids = numpy.asarray([random.randint(1, 100)])
    print(f"INFO (vectordb_faiss.clip_add_image): ids", ids)
    # WTF WHY DID THIS STOP WORKING index_clip.add_with_ids(image_embedding, ids)
    # Return ID?
    print(f"INFO (vectordb_faiss.clip_add_image): index.ntotal", index_clip.ntotal)
    print(f"INFO (vectordb_faiss.clip_add_image): index", index_clip)
    # OPTIMIZE: re-save index
    save_index(index_clip, index_clip_save_path)

def index_clip_search_images_by_text(text_query):
    print("INFO (vectordb_faiss:clip_search_images_by_text): query", text_query)
    text_embedding = index_clip_model.encode([text_query])
    # faiss.normalize_L2(text_embedding) # tbh, not entirely sure why/if this is needed. copied from openai clip tutorial
    print("INFO (vectordb_faiss:clip_search_images_by_text): text_embedding", text_embedding.shape)
    num_returned_results = 5 # what should this be?
    probabilities, ids = index_clip.search(text_embedding, num_returned_results)
    probabilities = probabilities[0]
    ids = ids[0]
    print("INFO (vectordb_faiss:clip_search_images_by_text): probabilities", probabilities)
    print("INFO (vectordb_faiss:clip_search_images_by_text): ids", ids)
    # --- join probabilities/ids (convert the numpy float to a Python float to be handled properly when JSON serialized)
    locations = list(map(lambda o: { "score": float(o[0]), "document_id": int(o[1]) }, list(zip(probabilities, ids))))
    # --- filter -1s
    return list(filter(lambda o: o["document_id"] > 0, locations))

# --- documents
async def index_documents_add_text(session, text, document_id=None, document_content_id=None):
    print("INFO (vectordb_faiss:index_documents_add_text): start")
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- save as .npy file to s3 as backup
    numpy_tensor_bytearray = write_tensor_to_bytearray(text_embedding_tensor)
    npy_file_key = f"index_documents_{uuid.uuid4()}.npy"
    s3_upload_file_bytes(npy_file_key, numpy_tensor_bytearray)
    # --- save embedding (we're doing an execute() + insert() so we can retrieve an id, not possible with add())
    print("INFO (vectordb_faiss:index_documents_add_text): save embedding")
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
    ids = numpy.array([embedding_id], dtype="int64") # idk, people say it takes int64 (https://github.com/99sbr/semantic-search-with-sbert/issues/1)
    print("INFO (vectordb_faiss:index_documents_add_text): index", index_documents)
    # printing values for this assert thats throwing https://github.com/facebookresearch/faiss/blob/af25054e2d0a7cda067c600ecf9b20b7b64e44c5/faiss/python/class_wrappers.py#L247
    print("INFO (vectordb_faiss:index_documents_add_text): index with ids", text_embedding_tensor.shape, ids)
    # WTF WHY DID THIS STOP WORKING index_documents.add_with_ids(text_embedding_tensor, ids)
    # OPTIMIZE: re-save index
    print("INFO (vectordb_faiss:index_documents_add_text): save index")
    save_index(index_documents, index_documents_save_path)

# --- sentences
async def index_sentences_add_text(session, text, document_id=None, document_content_id=None):
    print("INFO (vectordb_faiss:index_sentences_add_text): start")
    # --- get embedding
    text_embedding_tensor = gpt_embedding(text) # now returns as numpy array
    # --- save as .npy file to s3 as backup
    numpy_tensor_bytearray = write_tensor_to_bytearray(text_embedding_tensor)
    npy_file_key = f"index_sentences_{uuid.uuid4()}.npy"
    s3_upload_file_bytes(npy_file_key, numpy_tensor_bytearray)
    # --- save embedding
    print("INFO (vectordb_faiss:index_sentences_add_text): save embedding")
    embedding_query = await session.execute(
        insert(Embedding)
            .values(
                document_id=document_id,
                document_content_id=document_content_id,
                encoded_model="gpt3",
                encoded_model_engine=gpt_vars()["ENGINE_EMBEDDING"],
                encoding_strategy="text",
                text=text,
                npy_url=s3_get_file_url(npy_file_key)
            ).returning(Embedding.id)
    )
    embedding_id = embedding_query.scalar_one_or_none()
    # --- add to index (single item indexing means 1, dimensions?)
    ids = numpy.array([embedding_id], dtype="int64") # idk, people say it takes int64 (https://github.com/99sbr/semantic-search-with-sbert/issues/1)
    print("INFO (vectordb_faiss:index_sentences_add_text): index with ids", text_embedding_tensor.shape, ids)
    # WTF WHY DID THIS STOP WORKING index_sentences.add_with_ids(text_embedding_tensor, ids)
    # OPTIMIZE: re-save index
    print("INFO (vectordb_faiss:index_sentences_add_text): save index")
    save_index(index_sentences, index_sentences_save_path)
