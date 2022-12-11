from enum import Enum
import sqlalchemy as sa
import numpy as np
from sqlalchemy.orm import joinedload, Session
import pinecone

from dbs.sa_models import AIActionLock, Case
from dbs.vectordb_pinecone import VECTOR_INDEX_ID
from models.clip import clip_text_embedding, clip_image_embedding
from models.gpt import gpt_embedding
from models.sentence import sentence_encode_embeddings


class AI_ACTIONS(Enum):
    document_similarity_image_embed = 'document_similarity_image_embed'
    document_similarity_text_sentence_embed = 'document_similarity_text_sentence_embed'
    document_similarity_text_sentences_20_embed = 'document_similarity_text_sentences_20_embed'
    document_similarity_text_max_size_embed = 'document_similarity_text_max_size_embed'
    case_similarity_text_sentence_search = 'case_similarity_text_sentence_search'
    case_similarity_text_sentences_20_search = 'case_similarity_text_sentences_20_search'
    case_similarity_text_max_size_search = 'case_similarity_text_max_size_search'
    case_similarity_text_to_image_search = 'case_similarity_text_to_image_search'

class AI_MODELS(Enum):
    all_MiniLM_L6_v2 = 'all-MiniLM-L6-v2'
    text_similarity_ada_001 = 'text-similarity-ada-001'
    text_similarity_curie_001 = 'text-similarity-curie-001'
    text_similarity_davinci_001 = 'text-similarity-davinci-001'
    ViT_L_14_336px = 'ViT-L/14@336px'

class DISTANCE_METRIC(Enum):
    cosine = 'cosine'
    dot = 'dot'
    euclidian = 'euclidian'


class AIActionAgent():
    """AI Action Agent, loaded to encode/query/upsert appropriately"""
    action: AI_ACTIONS = None
    model_name: str = None # TODO: AI_MODELS
    _ai_action_locks: AIActionLock = None
    _case: Case = None
    _model_distance_metric: str = None
    _model_embed_dimensions: int = None
    _params: dict = None
    _vector_index_id: VECTOR_INDEX_ID = None
    def __init__(self, action: AI_ACTIONS, case, model_name):
        self.action = action
        self.model_name = model_name
        self._case = case
    def encode_text(self):
        pass # defined by w/ each inheriting class
    def encode_image(self):
        pass # defined by w/ each inheriting class
    def get_vector_index(self):
        return pinecone.Index(self._vector_index_id.value)
    def query_search_vectors(self, query_text, query_image=None, query_filters={}, top_k=12, score_max=1, score_min=0, score_min_diff_percent=None, score_max_diff_percent=None):
        # --- vector
        vectors = self.encode_text([query_text])
        if (len(vectors) == 0): return []
        vector = vectors[0]
        if (hasattr(vector, 'tolist')):
            vector = vector.tolist()
        # --- filter
        filters = {}
        if (query_filters != None):
            filters.update(query_filters)
        if (self._case.uuid != None):
            filters.update({ "case_uuid": { "$eq": str(self._case.uuid) } })
        # --- query for vector
        print(f'INFO (AIActionAgent:query_search_vectors): querying "{self.model_name}" on index "{self._vector_index_id}"', filters)
        query_results = self.get_vector_index().query(
            vector=vector,
            top_k=top_k,
            include_values=False,
            includeMetadata=True,
            filter=filters)
        # --- rank sort & vectors
        vectors = query_results['matches']
        print(f'INFO (AIActionAgent:query_search_vectors): "{self.model_name}" vectors', vectors[:5], '...')
        if (score_max != None and len(vectors) > 0):
            vectors = list(filter(lambda m: m['score'] < score_max, vectors))
        if (score_min != None and len(vectors) > 0):
            vectors = list(filter(lambda m: m['score'] > score_min, vectors))
        if (score_max_diff_percent != None and len(vectors) > 0):
            highest_score = vectors[0].score
            vectors = list(filter(lambda m: m['score'] > (highest_score - (highest_score * score_max_diff_percent)), vectors))
        if (score_min_diff_percent != None and len(vectors) > 0):
            lowest_score = vectors[0].score
            vectors = list(filter(lambda m: m['score'] < (lowest_score + (lowest_score * score_min_diff_percent)), vectors))
        print(f'INFO (AIActionAgent:query_search_vectors): "{self.model_name}" vectors filtered') # vectors
        return vectors

# AIActionAgent Classes
class AIActionAgent_AllMiniLML6v2(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 384
        self._vector_index_id = VECTOR_INDEX_ID.documents_text_384
    def encode_text(self, sentences):
        embeddings_arr = sentence_encode_embeddings(sentences)
        return embeddings_arr
    def encode_image(self):
        pass

class AIActionAgent_TextSimilarityAda001(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 1024
        self._vector_index_id = VECTOR_INDEX_ID.documents_text_1024
    def encode_text(self, text_statements):
        embeddings_arr = gpt_embedding(text_statements, engine=self.model_name) # returns numpy array
        return embeddings_arr
    def encode_image(self):
        pass
class AIActionAgent_TextSimilarityCurie001(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.euclidian
        self._model_embed_dimensions = 4096
        self._vector_index_id = VECTOR_INDEX_ID.documents_text_4096
    def encode_text(self, text_statements):
        embeddings_arr = gpt_embedding(text_statements, engine=self.model_name) # returns numpy array
        return embeddings_arr
    def encode_image(self):
        pass

class AIActionAgent_TextSimilarityDavinci001(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.euclidian
        self._model_embed_dimensions = 12288
        self._vector_index_id = VECTOR_INDEX_ID.documents_text_12288
    def encode_text(self, text_statements):
        embeddings_arr = gpt_embedding(text_statements, engine=self.model_name) # returns numpy array
        return embeddings_arr
    def encode_image(self):
        pass

class AIActionAgent_ViTL14336px(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 768
        self._vector_index_id = VECTOR_INDEX_ID.documents_clip_768
    def encode_text(self, text_statements):
        embeddings_arr = clip_text_embedding(text_statements) # now returns as numpy array
        return embeddings_arr
    def encode_image(self, image_file_urls):
        embeddings_arr = clip_image_embedding(image_file_urls)
        return embeddings_arr


# TODO: how the f can we just initialize a AIActionAgent class off the bat w/ this setup
async def create_ai_action_agent(session: Session, action: AI_ACTIONS, case_id: int):
    case_query = await session.execute(
        sa.select(Case)
            .options(joinedload(Case.ai_action_locks))
            .where(Case.id == case_id))
    case = case_query.scalars().first()
    ai_action_locks = case.ai_action_locks
    # 1. find action config/lock relevant
    for ai_action_lock in ai_action_locks:
        # ... if a match
        if action.value == ai_action_lock.action: # TODO: figure out if we should instead case to enum
            # ... return the model class
            model_name = ai_action_lock.model_name
            match model_name:
                case AI_MODELS.all_MiniLM_L6_v2.value:
                    return AIActionAgent_AllMiniLML6v2(action, case, model_name)
                case AI_MODELS.text_similarity_ada_001.value:
                    return AIActionAgent_TextSimilarityAda001(action, case, model_name)
                case AI_MODELS.text_similarity_curie_001.value:
                    return AIActionAgent_TextSimilarityCurie001(action, case, model_name)
                case AI_MODELS.text_similarity_davinci_001.value:
                    return AIActionAgent_TextSimilarityDavinci001(action, case, model_name)
                case AI_MODELS.ViT_L_14_336px.value:
                    return AIActionAgent_ViTL14336px(action, case, model_name)
    raise f'No AIActionAgent found for action: {action.value}'
