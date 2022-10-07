import faiss
import os
import numpy
import random
from sentence_transformers import SentenceTransformer
from gideon_clip import clip_vars, clip_image_embedding
from gideon_utils import get_file_path

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

# clip_image_model = SentenceTransformer('clip-ViT-L-14') # TODO: use @336 variant of L/14
clip_image_model = SentenceTransformer('clip-ViT-B-32') # doing this for now bc less memory usage?
faiss_index_clip_path = get_file_path("../indexed/faiss/clip.index")


# FAISS INDEX = IMAGES
def faiss_build_index():
    # IF INDEX SAVED
    if os.path.isfile(faiss_index_clip_path):
        built_index = faiss.read_index(faiss_index_clip_path)
    # IF NOT, BUILD
    else:
        # --- get future tensor dimensions for index params
        image_index_embedding_sample = clip_image_model.encode([get_file_path("../documents/gideon.png")])
        # --- build index
        print("INFO (gideon_faiss.py:faiss_build_index): shape =", image_index_embedding_sample.shape)
        # IVF_VORONI_CLUSTERS = 39 # only needed if we're doing ann styled indexes
        DIMENSIONS = image_index_embedding_sample.shape[1]
        print("INFO (gideon_faiss.py:faiss_build_index): DIMENSIONS =", DIMENSIONS)
        # FYI: If we're using an inverted index like IFV, we have to train i think to rebuild the top level indexes, otherwise it's trained
        # FYI: Only IVF indexes allow add_with_ids, L2 does not. Flat is a storage type. 
        # FYI: Not using a IVF index first means, means we're doing "exchaustive" search which may be better anyways for the legal domain since it's not excluding any result
        # FYI: IDMap + Flat means we can get knn exhaustive search w/ add_with_ids 
        built_index = faiss.index_factory(DIMENSIONS, "IDMap,Flat") # "Flat" "IVF4096,Flat" f"IVF{DIMENSIONS},Flat" f"IVF{IVF_VORONI_CLUSTERS},Flat"
    # RETURN (print some info to check)
    print("INFO (gideon_faiss.py:faiss_build_index): is_trained", built_index.is_trained)
    print("INFO (gideon_faiss.py:faiss_build_index): ntotal", built_index.ntotal)
    return built_index
# --- at startup, build index for images/text CLIP model
index = faiss_build_index()

def faiss_save_index():
    faiss.write_index(index, faiss_index_clip_path)

# FAISS UTILS
# filter is stricter w/ CLIP model bc similarity score variance is less
def filter_image_locations_within_top_prob_diff(image_locations, percentage_diff=0.02):
    print('INFO (gideon_faiss.py:filter_image_locations_within_top_prob_diff)', image_locations)
    lowest_score = image_locations[0]["score"]
    filtered_results = []
    for sr in image_locations:
        diff = (lowest_score * percentage_diff)
        if sr["score"] < (lowest_score + diff):
            filtered_results.append(sr)
    return filtered_results


# FAISS METHODS
def faiss_add_image(image_filepaths, filename):
    print(f"INFO (gideon_faiss.py:faiss_add_image): '{filename}'")
    image_embedding = clip_image_model.encode(image_filepaths)
    print(f"INFO (gideon_faiss.py:faiss_add_image): shape", image_embedding.shape)
    # FYI: we have to treat ids as a numpy.array() bc code within checks for shape property, not array length
    # https://github.com/facebookresearch/faiss/blob/c5b49b79df57cab7b7890c28f0ee5cb7329cbddd/faiss/python/class_wrappers.py#L621
    # TODO: connect w/ database ids
    ids = numpy.asarray([random.randint(1, 100)])
    print(f"INFO (gideon_faiss.py:faiss_add_image): ids", ids)
    index.add_with_ids(image_embedding, ids)
    # Return ID?
    print(f"INFO (gideon_faiss.py:faiss_add_image): index.ntotal", index.ntotal)
    print(f"INFO (gideon_faiss.py:faiss_add_image): index", index)
    # OPTIMIZE: re-save index
    faiss_save_index()

def faiss_search_images(text_query):
    print("INFO (gideon_faiss.py:faiss_search_images): query", text_query)
    text_embedding = clip_image_model.encode([text_query])
    # faiss.normalize_L2(text_embedding) # tbh, not entirely sure why/if this is needed. copied from openai clip tutorial
    print("INFO (gideon_faiss.py:faiss_search_images): text_embedding", text_embedding.shape)
    num_returned_results = 5 # what should this be?
    probabilities, ids = index.search(text_embedding, num_returned_results)
    probabilities = probabilities[0]
    ids = ids[0]
    print("INFO (gideon_faiss.py:faiss_search_images): probabilities", probabilities)
    print("INFO (gideon_faiss.py:faiss_search_images): ids", ids)
    # --- join probabilities/ids (convert the numpy float to a Python float to be handled properly when JSON serialized)
    locations = list(map(lambda o: { "score": float(o[0]), "document_id": int(o[1]) }, list(zip(probabilities, ids))))
    # --- filter -1s
    return list(filter(lambda o: o["document_id"] > 0, locations))
