import openai
from env import env_get_open_ai_api_key
from models.gpt import gpt_completion, gpt_embedding, gpt_summarize
from gideon_utils import get_file_path, open_txt_file
from dbs.vectordb_pinecone import index_documents_text_query, get_document_content_from_search_vectors

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()

# QUERY
async def question_answer(session, query):
    print(f'INFO (question_answer.py): querying with question "{query}"')
    # 1. get similar vectors
    search_text_vectors = await index_documents_text_query(query)
    # 2. get embeddings/document content of those
    document_content = await get_document_content_from_search_vectors(session, search_text_vectors)
    print(f'INFO (question_answer.py): answering from {len(document_content)} document_content(s)...', document_content)
    # 3. run embedding sentences/text through prompts for summarization
    final_answer = None
    if len(document_content) > 0:
        answers = []
        # --- 3a. get answer from high similarity vectors
        for idx, dc in enumerate(document_content):
            prompt = open_txt_file(get_file_path('./prompts/prompt_answer_question.txt')).replace('<<PASSAGE>>', dc.text).replace('<<QUESTION>>', query)
            answer = gpt_completion(prompt,engine='text-davinci-002',max_tokens=150)
            print(f'INFO (question_answer.py): answer #{idx+1} = {answer}')
            answers.append(answer)
        # --- 3b. summarize answers
        final_answer = gpt_summarize('\n\n'.join(answers), engine='text-davinci-002')
    else:
        final_answer = 'Found nothing relevant to your question.'
    # 4. return answer/no answer
    print(f'INFO (question_answer.py): final_answer = "{final_answer}"')
    return final_answer
