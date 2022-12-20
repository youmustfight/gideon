import pydash as _

def location_from_search_vector_embedding(sv, all_embeddings):
    # using our search vector metadata, find the relevant embedding
    # TODO: isn't embeddings going to be a massave af list? probaby should be a query?
    embedding = _.find(all_embeddings, lambda e: e.id == int(sv['metadata']['embedding_id']))

    # --- form document/documentcontent
    if (hasattr(embedding, 'document_content') and hasattr(embedding.document_content, 'document')):
        return dict(
            case_id=embedding.case_id,
            document=embedding.document_content.document,
            document_content=embedding.document_content,
            image_file=embedding.document_content.image_file if embedding.document_content.image_file != None else None,
            score=sv['score'],
            score_metric="cosine")

    # --- form case_id
    elif (hasattr(embedding, 'case_id')):
        return dict(
            case_id=embedding.case_id,
            writing_id=embedding.writing_id,
            score=sv['score'],
            score_metric="cosine")
        
    # --- some embeddings don't have attrs (could be bad data. idk this feels weird)
    return None
