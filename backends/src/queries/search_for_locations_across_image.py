from vector_dbs.vectordb_pinecone import index_clip_search_images_by_text

def filter_image_locations_within_top_prob_diff(image_locations, percentage_diff=0.02):
    print('INFO (FaissIndexes:filter_image_locations_within_top_prob_diff)', image_locations)
    lowest_score = image_locations[0]["score"]
    filtered_results = []
    for sr in image_locations:
        diff = (lowest_score * percentage_diff)
        if sr["score"] < (lowest_score + diff):
            filtered_results.append(sr)
    return filtered_results


def search_for_locations_across_image(text_query):
    print('INFO (search_for_locations_across_image.py): query images via multi-modal', text_query)
    # SEARCH
    # --- search
    locations = index_clip_search_images_by_text(text_query)
    # --- sort & filter
    # locations = filter_image_locations_within_top_prob_diff(locations)
    # RETURN
    print('INFO (search_for_locations_across_image.py) done')
    return locations
