# ATTEMPT 2 USING DONUT PACKAGE
from donut import DonutModel
from PIL import Image
import torch

# SETUP
# https://towardsdatascience.com/ocr-free-document-understanding-with-donut-1acfbdf099be
# https://github.com/clovaai/donut/blob/master/app.py
# --- model + processor
# DONUT_MODEL_NAME = 'naver-clova-ix/donut-base-finetuned-cord-v2'
# model = DonutModel.from_pretrained(DONUT_MODEL_NAME)
# model.eval()


# METHODS
# # --- parsing
def donut_document_parser(pil_image):
  pass
  # print('INFO (donut.py:donut_document_parser): start', pil_image)
  # # --- load document image (run .save() method to get bytes)
  # # image = Image.open(image_bytes)
  # # --- compute
  # task_prompt = '<s_cord-v2>'
  # output = model.inference(image=pil_image, prompt=task_prompt)
  # # --- decode/format results
  # print(output)



# ATTEMPT 1: USING HUGGINGFACE TRANSFORMERS LIB
# import re
# from PIL import Image
# import requests
# from transformers import DonutProcessor, VisionEncoderDecoderModel
# import torch

# # SETUP
# # https://huggingface.co/docs/transformers/main/en/model_doc/donut
# # https://github.com/clovaai/donut
# # --- model + processor
# DONUT_MODEL_NAME = 'naver-clova-ix/donut-base-finetuned-cord-v2'
# processor = DonutProcessor.from_pretrained(DONUT_MODEL_NAME)
# model = VisionEncoderDecoderModel.from_pretrained(DONUT_MODEL_NAME)
# # enable gpu if possible
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model.to(device)


# # METHODS
# # --- parsing
# def donut_document_parser(image_bytes):
#   # --- load document image
#   # image = Image.open(requests.get(image_file_url, stream=True).raw)
#   image = Image.open(image_bytes)
#   # --- prepare decoder inputs
#   task_prompt = "<s_cord-v2>"
#   decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids
#   # --- process pixels
#   pixel_values = processor(image, return_tensors="pt").pixel_values
#   # --- compute
#   outputs = model.generate(
#       pixel_values.to(device),
#       decoder_input_ids=decoder_input_ids.to(device),
#       max_length=model.decoder.config.max_position_embeddings,
#       early_stopping=True,
#       pad_token_id=processor.tokenizer.pad_token_id,
#       eos_token_id=processor.tokenizer.eos_token_id,
#       use_cache=True,
#       num_beams=1,
#       bad_words_ids=[[processor.tokenizer.unk_token_id]],
#       return_dict_in_generate=True,
#   )
#   # --- decode
#   sequence = processor.batch_decode(outputs.sequences)[0]
#   sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
#   sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token
#   print('donut_document_parser')
#   print('donut_document_parser')
#   print(processor.token2json(sequence))
#   print('donut_document_parser')
#   print('donut_document_parser')