from gideon_faiss import faiss_search_images, filter_image_locations_within_top_prob_diff

def search_for_locations_across_image(text_query):
    print('INFO (search_for_locations_across_image.py): query images via multi-modal', text_query)
    # SEARCH
    # --- search
    locations = faiss_search_images(text_query)
    # --- sort & filter
    locations = filter_image_locations_within_top_prob_diff(locations)

    # RETURN
    print('INFO (search_for_locations_across_image.py) done')
    return locations
