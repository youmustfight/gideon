import pydash as _
from dbs.vectordb_pinecone import index_documents_sentences_query, get_embeddings_from_search_vectors

# SEARCH QUERY
async def search_for_locations_across_text(session, text_query):
    print(f"INFO (search_for_locations_across_text.py): query all documents via '{text_query}'")
    # 1. get similar vectors (TODO: allow for minimum string length so we don't skew short statements higher similarity)
    search_text_vectors = index_documents_sentences_query(text_query)
    # 2. convert to DocumentContent
    embeddings = await get_embeddings_from_search_vectors(session, search_text_vectors)
    # 3. create "locations" array showing score + document content (TODO: move query+query result into db tables)
    def map_vector_and_content(sv):
        sv_embedding = _.find(embeddings, lambda e: e.id == int(sv['metadata']['embedding_id']))
        # --- some embeddings don't have attrs (could be bad data)
        if (hasattr(sv_embedding, 'document_content') and hasattr(sv_embedding.document_content, 'document')):
            location = dict(
                document=sv_embedding.document_content.document,
                document_content=sv_embedding.document_content,
                score= sv['score'],
                score_metric="euclidean",
            )
            return location
    # 3b. map document_content to search results
    locations = list(map(map_vector_and_content, search_text_vectors))
    # ... and then filter out any 'None's
    locations = list(filter(lambda loc: loc != None, locations))
    # 4. return
    print('INFO (search_for_locations_across_text.py): locations', locations)
    return locations
