import pydash as _

def search_vector_to_location(sv, all_embeddings):
    sv_embedding = _.find(all_embeddings, lambda e: e.id == int(sv['metadata']['embedding_id']))
    # --- form document/documentcontent
    if (hasattr(sv_embedding, 'document_content') and hasattr(sv_embedding.document_content, 'document')):
        location = dict(
            case_id=int(sv['metadata']['case_id']),
            document=sv_embedding.document_content.document,
            document_content=sv_embedding.document_content,
            image_file=sv_embedding.document_content.image_file if sv_embedding.document_content.image_file != None else None,
            score=sv['score'],
            score_metric="cosine")
        return location
    # --- form case_id
    if (hasattr(sv_embedding, 'case_id')):
        location = dict(
            case_id=int(sv['metadata']['case_id']),
            score=sv['score'],
            score_metric="cosine")
        return location
    # --- some embeddings don't have attrs (could be bad data)
