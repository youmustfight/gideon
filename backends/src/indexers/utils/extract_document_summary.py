import math
from models.gpt import gpt_summarize

def extract_document_summary(document_text):
  # summarize (change summary length based on document text)
  document_text_length = len(document_text)
  max_length = min(2000, math.floor(document_text_length / 4))
  print(f'INFO (extract_document_summary): document_text_length: {document_text_length} / max_length: {max_length}')
  summary = gpt_summarize(document_text, max_length=max_length)
  # return
  return summary