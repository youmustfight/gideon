import textwrap
from indexers.utils.text_contains_mentions_of_slavery import text_contains_mentions_of_slavery
from models.gpt import gpt_completion, GTP3_COMPLETION_MODEL_ENGINE_DAVINCI_002, GTP_COMPLETION_MODEL
from models.gpt_prompts import gpt_prompt_summary_concise, gpt_prompt_citing_slavery_summary, GPT_NULL_PHRASE

def extract_document_citing_slavery_summary(document_text):
    print("INFO (extract_document_citing_slavery_summary): start ")
    # summarize (change summary length based on document text)
    # TODO: probably a better way but seems to work?
    # SUMMARIZE CHUNKS
    summary_chunks = []
    summary_chunks_mentions_slavery = False
    chunks = textwrap.wrap(document_text, 3500)
    for chunk in chunks:
        # --- check for slavery references
        # In our prompt, we have a consistent text pattern for a no-match situation, so then we skip
        # if GPT_NULL_PHRASE not in specific_summary_chunk:
        if text_contains_mentions_of_slavery(chunk):
            specific_summary_chunk = gpt_completion(
                engine=GTP3_COMPLETION_MODEL_ENGINE_DAVINCI_002,
                max_tokens=500,
                prompt=gpt_prompt_citing_slavery_summary.replace('<<SOURCE_TEXT>>', chunk))
            print("INFO (extract_document_citing_slavery_summary): specific_summary_chunk ", specific_summary_chunk)
            summary_chunks.append(specific_summary_chunk)
            summary_chunks_mentions_slavery = True
        else:
            # Re-run without focus on slavery so we get context about information in this chunk
            # FYI: did this bc sections of 'Alfred v. State, 32 Tenn. 581, 2 Swan 581 (1852).' didn't talk about slavery but were important to overall context
            general_summary_chunk = gpt_completion(
                engine=GTP3_COMPLETION_MODEL_ENGINE_DAVINCI_002,
                max_tokens=500,
                prompt=gpt_prompt_summary_concise.replace('<<SOURCE_TEXT>>', chunk))
            print("INFO (extract_document_citing_slavery_summary): general_summary_chunk ", general_summary_chunk)
            summary_chunks.append(general_summary_chunk)

    # FINAL SUMMARY
    if len(summary_chunks) == 1 and summary_chunks_mentions_slavery == True:
        return summary_chunks[0]
    elif len(summary_chunks) > 1 and summary_chunks_mentions_slavery == True:
        summary_joined = " ".join(summary_chunks)
        print("INFO (extract_document_citing_slavery_summary): returning final completion")
        return gpt_completion(
            engine=GTP_COMPLETION_MODEL,
            max_tokens=500,
            prompt=gpt_prompt_citing_slavery_summary.replace('<<SOURCE_TEXT>>', summary_joined))
    else:
        print("INFO (extract_document_citing_slavery_summary): returning None")
        return None
