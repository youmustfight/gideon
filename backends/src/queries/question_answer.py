import openai
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from env import env_get_open_ai_api_key
from gideon_gpt import gpt_completion, gpt_embedding, gpt_summarize
from gideon_utils import get_file_path, open_txt_file
from dbs.sa_models import DocumentContent, Embedding
from dbs.vectordb_pinecone import index_documents_text_query

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()

# QUERY
async def question_answer(session, query):
    print(f'INFO (question_answer.py): querying with question "{query}"')
    # 1. get similar vectors
    search_text_vectors = await index_documents_text_query(query)
    # 1b. filter for vectors that were close % within top choice
    # 2. get embeddings of those
    search_text_embedding_ids = list(map(lambda v: int(v['metadata']['embedding_id']), search_text_vectors))
    print(f'INFO (question_answer.py): search_text_embedding_ids =', search_text_embedding_ids)
    embedding_query = await session.execute(
        sa.select(Embedding)
            .options(joinedload(Embedding.document_content))
            .where(Embedding.id.in_(search_text_embedding_ids))
    )
    embeddings = embedding_query.scalars().all()
    print(f'INFO (question_answer.py): answering from {len(embeddings)} embeddings(s)...', embeddings)
    document_content = list(map(lambda e: e.document_content, embeddings))
    # SUMMARIZE ANSWER
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
    # ANSWER RESPONSE
    print(f'INFO (question_answer.py): final_answer = "{final_answer}"')
    return final_answer
