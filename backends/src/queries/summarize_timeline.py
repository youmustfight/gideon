import datetime
from models.gpt import gpt_completion, gpt_vars
import openai
import sqlalchemy as sa
from sqlalchemy.orm import subqueryload

from dbs.sa_models import serialize_list, Document
from dbs.vectordb_pinecone import get_document_content_from_search_vectors
from env import env_get_open_ai_api_key
from files.file_utils import get_file_path, open_txt_file

# SETUP
# --- OpenAI
openai.api_key = env_get_open_ai_api_key()

# EXTRACT TIMELINE
async def summarize_timeline(documents):
    print(f'INFO (summarize_timeline.py): getting event timeline..."')

    # separate each source into a chronological list of events
    completion_events = []
    documents = documents.scalars().all()
    for document in documents:
        for content in document.content[:3]: # TODO Anna: remove slice after testing
            if content.text is not None:
                # set up prompt
                prompt = open_txt_file(get_file_path('./prompts/prompt_timeline.txt')).replace('<<SOURCE_TEXT>>', content.text)
                prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
                # extract timeline
                print('INFO (summarize_timeline.py): prompt\n\n', prompt)
                completion_events.append(gpt_completion(
                    prompt, max_tokens=500, engine=gpt_vars()['ENGINE_COMPLETION']
                ))

    # format events: split each into a date, description, documents involved
    events = []
    for completion_event in completion_events:
        for line in completion_event.split('\n'):
            if line != '' and line is not None:
                events.append(line)

    # remove events with no dates

    # order into chronological order

    # merge events from different sources that happened on the same date?

    print('INFO (summarize_timeline.py): events\n\n', events)
    return events
