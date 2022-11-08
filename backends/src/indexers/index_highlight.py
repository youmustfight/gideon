import json
from models.gpt import gpt_vars
from models.gpt import gpt_embedding
from gideon_utils import get_file_path
import time


def index_highlight(
    filename,
    user,
    document_text_vectors_by_sentence_start_index,
    document_text_vectors_by_sentence_end_index,
    highlight_text,
    note_text,
):
    print("INFO (index_highlight.py): started")
    # PROCESS FILE + PROPERTIES
    output_filepath = get_file_path('../indexed/highlights/highlight-{user}-{ms}.json'.format(ms=time.time(),user=user))
    # Setup Vars
    ai_tool = "gpt3"
    ai_models = gpt_vars()

    # EMBEDDINGS
    # create embeddings: highlight_text
    highlight_text_vector = gpt_embedding(highlight_text.encode(encoding='ASCII',errors='ignore').decode())
    # create embeddings: note_text
    note_text_vector = gpt_embedding(note_text.encode(encoding='ASCII',errors='ignore').decode())

    # SAVE FILE
    highlight = {
        "ai_tool": ai_tool,
        "ai_models": ai_models,
        "filename": filename,
        "user": user,
        "document_text_vectors_by_sentence_start_index": document_text_vectors_by_sentence_start_index,
        "document_text_vectors_by_sentence_end_index": document_text_vectors_by_sentence_end_index,
        "highlight_text": highlight_text,
        "highlight_text_vector": highlight_text_vector,
        "note_text": note_text,
        "note_text_vector": note_text_vector,
    }
    with open(output_filepath, 'w') as outfile:
        json.dump(highlight, outfile, indent=2)
    print('INFO (index_highlight.py): saved file')

    # RETURN
    return highlight