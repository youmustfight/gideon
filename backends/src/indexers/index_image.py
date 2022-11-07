import json
from sentence_transformers import SentenceTransformer
from gideon_clip import clip_classifications, clip_image_embedding, clip_vars
from gideon_utils import get_file_path
from dbs.vectordb_pinecone import index_clip_add_image

# INDEX_IMAGE
async def index_image(filename):
    print("INFO (index_image.py): started")
    input_filepath = get_file_path("../documents/{filename}".format(filename=filename))
    output_filepath = get_file_path('../indexed/{filename}.json'.format(filename=filename))
    # PROCESS FILE + PROPERTIES
    # processing n/a
    image_file_paths = [input_filepath]
    # Setup Vars
    ai_tool = "clip"
    ai_models = clip_vars()
    document_type = ''
    document_type_classifications = []
    document_summary = ''
    document_summary_classifications = []
    # TODO: document_image_feature_vector ??? = []
    def map_prediction_text(prediction):
        return prediction['classification']

    # CLIP
    # --- vectors... for search... inspired by... https://adeshg7.medium.com/build-your-own-search-engine-using-openais-clip-and-fastapi-part-1-89995aefbcdd
    print('INFO (index_image.py): add vector to faiss index', document_summary_classifications)
    index_clip_add_image([input_filepath], filename)  
    
    # --- document type (ex: mug shot, crime scene, etc. high level)
    document_type_classifications = []
    c_type = clip_classifications(
        classifications=["a mugshot photo", "a photo of a crime scene"],
        image_file_paths=image_file_paths,
        min_similarity=0.6
    )
    document_type_classifications = document_type_classifications + c_type[0]
    print('INFO (index_image.py): document_type_classifications', document_type_classifications)
    document_type = ", ".join(map(map_prediction_text, document_type_classifications))
    print('INFO (index_image.py): document_type', document_type)

    # --- document summary (multiple breakdowns w/ contrast between classifications)
    document_summary_classifications = []
    c_time_of_day = clip_classifications(
        classifications=["a photo during the day", "a photo during the night"],
        image_file_paths=image_file_paths,
        min_similarity=0.6
    )
    document_summary_classifications = document_summary_classifications + c_time_of_day[0]
    c_mug_shot = clip_classifications(
        classifications=["a photo of a person", "a photo containing multiple people", "a photo containing no people", "a photo containing documents"],
        image_file_paths=image_file_paths,
        min_similarity=0.6
    )
    document_summary_classifications = document_summary_classifications + c_mug_shot[0]
    c_environment = clip_classifications(
        classifications=["a photo indoors", "a photo outdoors"],
        image_file_paths=image_file_paths,
        min_similarity=0.6
    )
    document_summary_classifications = document_summary_classifications + c_environment[0]
    print('INFO (index_image.py): document_summary_classifications', document_summary_classifications)
    document_summary = ", ".join(map(map_prediction_text, document_summary_classifications))
    print('INFO (index_image.py): document_summary', document_summary)

    # FINISH
    # --- save file
    with open(output_filepath, 'w') as outfile:
        json.dump({
            "ai_tool": ai_tool,
            "ai_models": ai_models,
            "document_summary": document_summary,
            "document_summary_classifications": document_summary_classifications,
            "document_type": document_type,
            "document_type_classifications": document_type_classifications,
            "filename": filename,
            "format": "image", # todo: mime/type
            "index_type": "discovery",
        }, outfile, indent=2)
    print('INFO (index_image.py): saved file')


# RUN
if __name__ == '__main__':
    # affidavit-search-seize.pdf
    filename = input("Filename To Process: ")
    index_image(filename)
