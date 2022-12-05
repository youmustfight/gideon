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
        top_k=12,
        score_max=1.2,
        score_min_diff_percent=0.15)

    # 2. get embeddings/document content of those
    document_content = await get_document_content_from_search_vectors(session, search_vectors)
    print(f'INFO (question_answer.py): answering from {len(document_content)} document_content(s)...', document_content)

    # 3. run embedding sentences/text through prompts for summarization
    final_answer = None
    if len(document_content) > 0:
        answers = []
        # --- 3a. get answer from high similarity vectors
        for idx, dc in enumerate(document_content):
            prompt = gpt_prompt_answer_question.replace('<<PASSAGE>>', dc.text).replace('<<QUESTION>>', query_text)
            answer = gpt_completion(prompt,max_tokens=150)
            print(f'INFO (question_answer.py): answer #{idx+1} = {answer}')
            answers.append(answer)
        # --- 3b. summarize answers
        final_answer = gpt_summarize('\n\n'.join(answers), max_length=650)
    else:
        final_answer = 'Found nothing relevant to your question.'

    # 4. return answer/no answer
    print(f'INFO (question_answer.py): final_answer = "{final_answer}"')
    return final_answer
