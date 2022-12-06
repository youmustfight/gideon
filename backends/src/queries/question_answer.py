import ray
from aia.agent import AI_ACTIONS, create_ai_action_agent
from models.gpt import gpt_completion, gpt_summarize
from models.gpt_prompts import gpt_prompt_answer_question
from dbs.vectordb_pinecone import get_document_content_from_search_vectors

# QUERY
async def question_answer(session, query_text, case_id):
    print(f'INFO (question_answer.py): querying with question "{query_text}"')
    # 1. get similar vectors
    aigent_location_text_searcher = await create_ai_action_agent(session, action=AI_ACTIONS.case_similarity_text_max_size_search, case_id=case_id)
    search_vectors = aigent_location_text_searcher.query_search_vectors(
        query_text,
        query_filters={ "string_length": { "$gt": 480 } },
        top_k=8,
        score_max=1.2,
        score_min_diff_percent=0.15)

    # 2. get embeddings/document content of those
    document_content = await get_document_content_from_search_vectors(session, search_vectors)
    print(f'INFO (question_answer.py): answering from {len(document_content)} document_content(s)...', document_content)

    # V1 SYNC (75~180 sec)
    # V2 ASYNC w/ PARALLEL PROCESSORS (not threads) (40~60 sec)
    @ray.remote
    def query_for_answer(passage_text, query_text):
        prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', passage_text).replace('<<QUESTION>>', query_text)
        answer = gpt_completion(prompt,max_tokens=150)
        return answer
    # 3a. run parallelized
    final_answer_futures = list(
        map(lambda dc: query_for_answer.remote(dc.text, query_text), document_content))
    results = ray.get(final_answer_futures)
    # 3b. summarize
    final_answer = gpt_summarize('\n\n'.join(results), max_length=650)

    # 4. return answer/no answer
    print(f'INFO (question_answer.py): final_answer = "{final_answer}"')
    return final_answer
