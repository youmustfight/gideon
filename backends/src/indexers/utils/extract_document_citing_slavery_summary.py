import textwrap
from models.gpt import gpt_completion, gpt_summarize, gpt_vars
from models.gpt_prompts import gpt_prompt_citing_slavery_summary

ESCAPE_PHRASE = 'No mention of slavery'

def extract_document_citing_slavery_summary(document_text):
  # summarize (change summary length based on document text)
  # TODO: probably a better way but seems to work?
  summary_chunks = []
  chunks = textwrap.wrap(document_text, 4000)
  for chunk in chunks:
    summary_chunk = gpt_completion(
      engine=gpt_vars()['ENGINE_COMPLETION'],
      max_tokens=500,
      prompt=gpt_prompt_citing_slavery_summary.replace('<<SOURCE_TEXT>>', chunk))
    # In our prompt, we have a consistent text pattern for a no-match situation, so then we skip
    print(summary_chunk)
    if ESCAPE_PHRASE not in summary_chunk:
      summary_chunks.append(summary_chunk)
  # return
  return None if len(summary_chunks) == 0 else " ".join(summary_chunks)
