import textwrap
from models.gpt import gpt_completion, gpt_summarize, gpt_vars

ESCAPE_PHRASE = 'No mention of slavery.'

def extract_document_citing_slavery_summary(document_text):
  # summarize (change summary length based on document text)
  prompt = """
  In the fewest words, summarize the context mentioning slaves in the following passage. If no mention of slavery exists, write '{ESCAPE_PHRASE}':

  PASSAGE: <<SOURCE_TEXT>>

  SUMMARY:
  """
  # TODO: probably a better way but seems to work?
  summary_chunks = []
  chunks = textwrap.wrap(document_text, 4000)
  for chunk in chunks:
    summary_chunk = gpt_completion(
      engine=gpt_vars()['ENGINE_COMPLETION'],
      max_tokens=500,
      prompt=prompt.replace('<<SOURCE_TEXT>>', chunk))
    # In our prompt, we have a consistent text pattern for a no-match situation, so then we skip
    print(summary_chunk)
    if ESCAPE_PHRASE not in summary_chunk:
      summary_chunks.append(summary_chunk)
  # return
  return None if len(summary_chunks) == 0 else " ".join(summary_chunks)
