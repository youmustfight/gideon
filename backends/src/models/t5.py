# DONT USE: T5 uses too much memory. Crahes container

# import requests
# from transformers import T5Tokenizer, T5ForConditionalGeneration

# https://github.com/google-research/text-to-text-transfer-transformer#released-model-checkpoints
# https://ai.googleblog.com/2021/10/introducing-flan-more-generalizable.html
# https://ai.googleblog.com/2020/02/exploring-transfer-learning-with-t5.html
# https://huggingface.co/google/flan-t5-large
# https://huggingface.co/google/flan-t5-xxl
# https://arxiv.org/pdf/2210.11416.pdf (pg 41, comparisons of models on different tasks. OH SHIT DATE UNDERSTANDING)
# maybe replace with https://www.together.xyz/blog/releasing-v1-of-gpt-jt-powered-by-open-source-ai
# model_name = 'google/flan-t5-large'

# Setup T5 tokenizer/model (should be pre-loaded via Dockerfile)
# tokenizer = T5Tokenizer.from_pretrained(model_name)
# model = T5ForConditionalGeneration.from_pretrained(model_name)


# def t5_completion(prompt, max_length=100, engine='TODO'):
  # V1 LOCAL MODEL
  # print(f'INFO (T5): t5_completion: {prompt[0:240]}...')
  # # tokenize prompt (gets rid of common words w/o meaning)
  # input_ids = tokenizer(prompt, return_tensors='pt').input_ids
  # # generate text  
  # outputs = model.generate(input_ids, max_length=max_length)
  # completion = tokenizer.decode(outputs[0])
  # # return
  # print(f'INFO (T5): t5_completion: {completion}')
  # return completion
  # V2 HOSTED MODEL ON SAGEMAKER