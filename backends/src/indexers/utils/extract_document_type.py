from models.gpt import gpt_completion
from models.gpt_prompts import gpt_prompt_document_type

def extract_document_type(document_text):
      return gpt_completion(
            gpt_prompt_document_type.replace('<<SOURCE_TEXT>>', document_text[0:11_000]),
            max_tokens=75
      )