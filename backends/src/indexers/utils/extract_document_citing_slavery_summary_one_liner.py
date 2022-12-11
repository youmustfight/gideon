from models.gpt import gpt_completion, GTP3_COMPLETION_MODEL_ENGINE
from models.gpt_prompts import gpt_prompt_citing_slavery_summary_one_liner

def extract_document_citing_slavery_summary_one_liner(document_text):
  # V2
  one_liner = gpt_completion(
      engine=GTP3_COMPLETION_MODEL_ENGINE,
      max_tokens=500,
      prompt=gpt_prompt_citing_slavery_summary_one_liner.replace('<<SOURCE_TEXT>>', document_text))
  
  # return
  return one_liner