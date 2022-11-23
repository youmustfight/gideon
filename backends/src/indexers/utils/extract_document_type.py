from files.file_utils import get_file_path, open_txt_file
from models.gpt import gpt_completion


def exact_document_type(document_text):
      return gpt_completion(
            open_txt_file(get_file_path('./prompts/prompt_document_type.txt')).replace('<<SOURCE_TEXT>>', document_text[0:11_000]),
            max_tokens=75
      )