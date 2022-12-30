from enum import Enum
from typing import List
import sqlalchemy as sa
import numpy as np
from sqlalchemy.orm import joinedload, Session
import pinecone

from dbs.sa_models import AIActionLock, Case, Organization
from dbs.vectordb_pinecone import VECTOR_INDEX_ID
from models.clip import clip_text_embedding, clip_image_embedding
from models.gpt import gpt_embedding
from models.sentence import sentence_encode_embeddings

# TODO: The relationships between actions is not at all obvious
# Ex: I already forgot that these document embedders are saving to indexes that search actions rely on
# It feels like these will quickly drift out of sync with each other as we add more and we need to partition indexes
class AI_ACTIONS(Enum):
    document_similarity_image_embed = 'document_similarity_image_embed'
    document_similarity_text_sentence_embed = 'document_similarity_text_sentence_embed'
    document_similarity_text_sentences_20_embed = 'document_similarity_text_sentences_20_embed'
    document_similarity_text_max_size_embed = 'document_similarity_text_max_size_embed'
    brief_facts_similarity_embed = 'brief_facts_similarity_embed'
    brief_facts_similarity_search = 'brief_facts_similarity_search'
    case_similarity_text_sentence_search = 'case_similarity_text_sentence_search'
    case_similarity_text_sentences_20_search = 'case_similarity_text_sentences_20_search'
    case_similarity_text_max_size_search = 'case_similarity_text_max_size_search'
    case_similarity_text_to_image_search = 'case_similarity_text_to_image_search'
    writing_similarity_embed = 'writing_similarity_embed'
    writing_similarity_search = 'writing_similarity_search'

class AI_MODELS(Enum):
    all_mpnet_base_v2 = 'all-mpnet-base-v2'
    all_MiniLM_L6_v2 = 'all-MiniLM-L6-v2' # DEPRECATED
    text_embedding_ada_002 = 'text-embedding-ada-002'
    text_similarity_ada_001 = 'text-similarity-ada-001' # DEPRECATED
    text_similarity_curie_001 = 'text-similarity-curie-001' # DEPRECATED
    text_similarity_davinci_001 = 'text-similarity-davinci-001' # DEPRECATED
    ViT_L_14_336px = 'ViT-L/14@336px'

class DISTANCE_METRIC(Enum):
    cosine = 'cosine'
    dot = 'dot'
    euclidian = 'euclidian'


class AIActionAgent():
    """AI Action Agent, loaded to encode/query/upsert appropriately"""
    ai_action: AI_ACTIONS = None
    index_id: str = None
    index_partition_id: str = None
    model_name: str = None
    _ai_action_locks: AIActionLock = None
    _model_distance_metric: str = None
    _model_embed_dimensions: int = None
    def __init__(self, ai_action: AI_ACTIONS, index_id, index_partition_id, model_name):
        self.ai_action = ai_action
        self.index_id = index_id
        self.index_partition_id = index_partition_id
        self.model_name = model_name
    def encode_text(self):
        pass # defined by w/ each inheriting class
    def encode_image(self):
        pass # defined by w/ each inheriting class
    def _get_vector_index(self):
        return pinecone.Index(self.index_id)
    def index_query(self, query_text=None, query_image=None, query_vectors=None, query_filters={}, top_k=12, score_max=1, score_min=0, score_min_diff_percent=None, score_max_diff_percent=None):
        # --- vector
        vectors = query_vectors or self.encode_text([query_text])
        if (len(vectors) == 0): return []
        vector = vectors[0]
        if (hasattr(vector, 'tolist')):
            vector = vector.tolist()
        # --- filters
        filters = {}
        # --- filters: pinecone
        if (query_filters != None):
            filters.update(query_filters)
        # --- query for vector
        print(f'INFO (AIActionAgent:index_query): querying with "{self.model_name}" on index "{self.index_id}"', filters)
        query_results = self._get_vector_index().query(
            namespace=self.index_partition_id,
            vector=vector,
            top_k=top_k,
            include_values=False,
            includeMetadata=True,
            filter=filters)
        # --- rank sort & vectors
        vectors = query_results['matches']
        print(f'INFO (AIActionAgent:index_query): "{self.model_name}" vectors', vectors[:5], '...')
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
        print(f'INFO (AIActionAgent:index_query): "{self.model_name}" vectors filtered') # vectors
        return vectors
    def index_upsert(self, vectors):
        # TODO: not sure if we should do this tbh since we save all the index info on the embedding model
        pass


# AIActionAgent Classes
class AIActionAgent_AllMiniLML6v2(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 384
    def encode_text(self, sentences):
        embeddings_arr = sentence_encode_embeddings(sentences)
        return embeddings_arr
    def encode_image(self):
        pass
class AIActionAgent_AllMpnetBaseV2(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 768
    def encode_text(self, sentences):
        embeddings_arr = sentence_encode_embeddings(sentences)
        return embeddings_arr
    def encode_image(self):
        pass

class AIActionAgent_TextEmbeddingAda002(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 1536
    def encode_text(self, text_statements):
        embeddings_arr = gpt_embedding(text_statements, engine=self.model_name) # returns numpy array
        return embeddings_arr
    def encode_image(self):
        pass
class AIActionAgent_TextSimilarityAda001(AIActionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_distance_metric = DISTANCE_METRIC.cosine
        self._model_embed_dimensions = 1024
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
    def encode_text(self, text_statements):
        embeddings_arr = clip_text_embedding(text_statements) # now returns as numpy array
        return embeddings_arr
    def encode_image(self, image_file_urls):
        embeddings_arr = clip_image_embedding(image_file_urls)
        return embeddings_arr


# TODO: how the f can we just initialize a AIActionAgent class off the bat w/ this setup
async def create_ai_action_agent(session: Session, action: AI_ACTIONS, ai_action_locks=None, case_id=None, organization_id=None):
    print(f'INFO (agent.py:create_ai_action_agent) create', action)
    aia_locks: List[AIActionLock] = ai_action_locks
    if aia_locks == None and case_id != None:
        case_query = await session.execute(
            sa.select(Case)
                .options(joinedload(Case.ai_action_locks))
                .where(Case.id == case_id))
        case = case_query.scalars().first()
        aia_locks = case.ai_action_locks
    elif aia_locks == None and organization_id != None:
        org_query = await session.execute(
            sa.select(Organization)
                .options(joinedload(Organization.ai_action_locks))
                .where(Organization.id == organization_id))
        organization = org_query.scalars().first()
        aia_locks = organization.ai_action_locks

    # 1. find action config/lock relevant
    for ai_action_lock in aia_locks:
        # ... if a match
        if action.value == ai_action_lock.action: # TODO: figure out if we should instead case to enum
            # ... return the model class
            model_name = ai_action_lock.model_name
            def get_ai_agent_for_model(model_name):
                match model_name:
                    # DEPRECATED
                    # case AI_MODELS.all_MiniLM_L6_v2.value:
                    #     return AIActionAgent_AllMiniLML6v2
                    case AI_MODELS.all_mpnet_base_v2.value:
                        return AIActionAgent_AllMpnetBaseV2
                    # DEPRECATED
                    # case AI_MODELS.text_similarity_ada_001.value:
                    #     return AIActionAgent_TextSimilarityAda001
                    case AI_MODELS.text_embedding_ada_002.value:
                        return AIActionAgent_TextEmbeddingAda002
                    # DEPRECATED
                    # case AI_MODELS.text_similarity_curie_001.value:
                    #     return AIActionAgent_TextSimilarityCurie001
                    # DEPRECATED
                    # case AI_MODELS.text_similarity_davinci_001.value:
                    #     return AIActionAgent_TextSimilarityDavinci001
                    case AI_MODELS.ViT_L_14_336px.value:
                        return AIActionAgent_ViTL14336px
            AIA = get_ai_agent_for_model(model_name)
            if (AIA):
                return AIA(
                    ai_action=action,
                    index_id=ai_action_lock.index_id,
                    index_partition_id=ai_action_lock.index_partition_id,
                    model_name=model_name,
                )
    raise f'No AIActionAgent found for action: {action.value}'


def generate_ai_action_locks(case_id = None, organization_id = None):
  return [
    # DOCUMENT EMBEDDING
    AIActionLock(
        action=AI_ACTIONS.document_similarity_text_sentence_embed.value,
        model_name=AI_MODELS.all_mpnet_base_v2.value,
        index_id=VECTOR_INDEX_ID.index_768_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_sentence_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.document_similarity_text_sentences_20_embed.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_sentences_20_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.document_similarity_text_max_size_embed.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_max_size_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.document_similarity_image_embed.value,
        model_name=AI_MODELS.ViT_L_14_336px.value,
        index_id=VECTOR_INDEX_ID.index_768_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_image_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    # CASE FACTS EMBED+SEARCH
    AIActionLock(
        action=AI_ACTIONS.brief_facts_similarity_embed.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.brief_facts_similarity_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.brief_facts_similarity_search.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.brief_facts_similarity_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    # CASE->DOCUMENTS SEARCH
    AIActionLock(
        action=AI_ACTIONS.case_similarity_text_sentence_search.value,
        model_name=AI_MODELS.all_mpnet_base_v2.value,
        index_id=VECTOR_INDEX_ID.index_768_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_sentence_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.case_similarity_text_sentences_20_search.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_sentences_20_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.case_similarity_text_max_size_search.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_text_max_size_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.case_similarity_text_to_image_search.value,
        model_name=AI_MODELS.ViT_L_14_336px.value,
        index_id=VECTOR_INDEX_ID.index_768_cosine.value,
        index_partition_id=AI_ACTIONS.document_similarity_image_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    # WRITING EMBED
    AIActionLock(
        action=AI_ACTIONS.writing_similarity_embed.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.writing_similarity_embed.value,
        case_id=case_id,
        organization_id=organization_id),
    AIActionLock(
        action=AI_ACTIONS.writing_similarity_search.value,
        model_name=AI_MODELS.text_embedding_ada_002.value,
        index_id=VECTOR_INDEX_ID.index_1536_cosine.value,
        index_partition_id=AI_ACTIONS.writing_similarity_embed.value,
        case_id=case_id,
        organization_id=organization_id),
  ]

