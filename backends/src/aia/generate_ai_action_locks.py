from aia.agent import AI_ACTIONS, AI_MODELS
from dbs.sa_models import AIActionLock

def generate_ai_action_locks(case_id = None):
  return [
    # EMBED
    AIActionLock(action=AI_ACTIONS.document_similarity_text_sentence_embed.value, model_name=AI_MODELS.all_MiniLM_L6_v2.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.document_similarity_text_sentences_20_embed.value, model_name=AI_MODELS.text_similarity_curie_001.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.document_similarity_text_max_size_embed.value, model_name=AI_MODELS.text_similarity_curie_001.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.document_similarity_image_embed.value, model_name=AI_MODELS.ViT_L_14_336px.value, params={}, case_id=case_id),
    # SEARCH
    AIActionLock(action=AI_ACTIONS.case_similarity_text_sentence_search.value, model_name=AI_MODELS.all_MiniLM_L6_v2.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.case_similarity_text_sentences_20_search.value, model_name=AI_MODELS.text_similarity_curie_001.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.case_similarity_text_max_size_search.value, model_name=AI_MODELS.text_similarity_curie_001.value, params={}, case_id=case_id),
    AIActionLock(action=AI_ACTIONS.case_similarity_text_to_image_search.value, model_name=AI_MODELS.ViT_L_14_336px.value, params={}, case_id=case_id),
  ]
