from transformers import T5Tokenizer, T5ForConditionalGeneration

model_name = "google/flan-t5-xxl"

# Setup T5 tokenizer/model (should be pre-loaded via Dockerfile)
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


def t5_completion(prompt, engine="TODO"):
  print(f'INFO (T5): t5_completion: {prompt[0:240]}...')
  # tokenize prompt (gets rid of common words w/o meaning)
  input_ids = tokenizer(prompt, return_tensors="pt").input_ids
  # generate text  
  outputs = model.generate(input_ids)
  completion = tokenizer.decode(outputs[0])
  # return
  print(f'INFO (T5): t5_completion: {completion}')
  return completion


