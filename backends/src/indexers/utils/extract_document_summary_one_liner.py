import math
from models.gpt import gpt_summarize
from models.gpt_prompts import gpt_prompt_summary_concise

def extract_document_summary_one_liner(document_text):
  # summarize (change summary length based on document text)
  document_text_length = len(document_text)
  max_length = 250
  print(f'INFO (extract_document_summary_one_liner): document_text_length', document_text_length)
  print(f'INFO (extract_document_summary_one_liner): max_length', max_length)
  summary = gpt_summarize(document_text, max_length=max_length, use_prompt=gpt_prompt_summary_concise)
  
  # return
  return summary