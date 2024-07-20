import asyncio
from ai.agents.ai_action_agent import AI_ACTIONS, create_ai_action_agent
from dbs.vectordb_pinecone import get_document_content_from_search_vectors, get_embeddings_from_search_vectors
from models.gpt import gpt_completion, gpt_summarize
from models.gpt_prompts import gpt_prompt_answer_question
from ai.requests.utils.location_from_search_vector_embedding import location_from_search_vector_embedding


# QUERY
async def question_answer(session, query_text, case_id=None, document_id=None, user_id=None):
    # 0. SETUP (filters to allow case or document focus)
    query_filters = {}
    if case_id != None:
        query_filters.update({ 'case_id': { '$eq': int(case_id) } })
    if document_id != None:
        query_filters.update({ 'document_id': { '$eq': int(document_id) } })
    print(f'INFO (question_answer.py): querying with question "{query_text}"', query_filters)
    
    # 1. get similar vectors
    aigent_location_text_searcher = await create_ai_action_agent(session, action=AI_ACTIONS.case_similarity_text_sentences_20_search, case_id=case_id, user_id=user_id)
    search_vectors = aigent_location_text_searcher.index_query(
        query_text,
        query_filters=query_filters,
        # query_filters={ "content_text_length": { "$gt": 480 } }, # DEPRECATED: idk if we need this anymore, tokenizing is better now and ensures min lengths
        top_k=5, # was 8, I feel like only focusing on high matches will get less noisy answers + be faster
        score_min=0.5,
        score_max=1.2,
        score_min_diff_percent=0.15)

    # 2. get embeddings/document content of those
    document_content = await get_document_content_from_search_vectors(session, search_vectors)
    text_search_embeddings = await get_embeddings_from_search_vectors(session, search_vectors)
    print(f'INFO (question_answer.py): answering from {len(document_content)} document_content(s)...', document_content)

    # 3. Query Question in Parts
    # # V1 SYNC (75~180 sec)
    # # V2 ASYNC w/ PARALLEL PROCESSORS USING RAY (not threads) (40~60 sec)
    # @ray.remote
    # async def query_for_answer(passage_text, query_text):
    #     prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', passage_text).replace('<<QUESTION>>', query_text)
    #     answer = gpt_completion(prompt,max_tokens=150)
    #     return answer
    # final_answer_futures = list(
    #     map(lambda dc: query_for_answer.remote(dc.text, query_text), document_content))
    # # V3 ASYNC w/ PARALLEL JOBS USING RQ (locally at sync speed, but in prod can parallelize w/ multiple instances)
    # V4 ASYNCIO CONCURRENCY (~50 sec)
    # --- tasks (only works bc they're async?)
    async def query_for_answer(passage_text, query_text):
        prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', passage_text).replace('<<QUESTION>>', query_text)
        answer = gpt_completion(prompt,max_tokens=150)
        return answer
    coroutine_tasks = map(lambda dc: query_for_answer(dc.text, query_text), document_content)
    print(f'INFO (question_answer.py): coroutines', coroutine_tasks)
    # --- results
    results = await asyncio.gather(*coroutine_tasks)

    # 3b. Summarize Final
    final_answer = gpt_summarize('\n\n'.join(results), max_length=650)
    # 3c. Locations for content that lead to summary
    locations = list(map(lambda sv: location_from_search_vector_embedding(sv, text_search_embeddings), search_vectors))
    locations = list(filter(lambda loc: loc != None, locations))

    # 4. return answer/no answer
    print(f'INFO (question_answer.py): final_answer = "{final_answer}"', locations)
    return final_answer, locations
