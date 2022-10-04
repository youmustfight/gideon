from gideon_utils import filter_formats, get_documents_json

# --- search
def search_for_image_locations_by_text_embedding(text_embedding):
    print('INFO (search_for_image_locations_by_text_embedding.py): query all documents for vector', text_embedding)
    # SETUP
    # --- files
    json_documents = get_documents_json()
    json_documents = filter_formats(["image"], json_documents)
    print('INFO (search_for_image_locations_by_text_embedding.py) done')
    return []
