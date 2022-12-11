from PIL import Image
import numpy as np
import requests
from transformers import CLIPProcessor, CLIPTokenizer, CLIPModel
import torch

# SETUP
CLIP_MODEL_NAME = 'openai/clip-vit-large-patch14-336'
# --- model + preprocess for images
ViTL14_336_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
ViTL14_336_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
ViTL14_336_tokenizer = CLIPTokenizer.from_pretrained(CLIP_MODEL_NAME)


# METHODS
# --- helpers
def _image_file_urls_to_files(image_file_urls_arr):
    return list(map(lambda image_file_url: Image.open(requests.get(image_file_url, stream=True).raw), image_file_urls_arr))

# --- embedding
def clip_text_embedding(text_arr):
    print('INFO (clip.py:clip_text_embedding): ', text_arr)
    with torch.no_grad():
        processed_text_arr = ViTL14_336_tokenizer(text=text_arr, padding=True, return_tensors="pt")
        text_embeddings = ViTL14_336_model.get_text_features(**processed_text_arr)
        # convert to list of float32 np arrays to be consistent
        text_embeddings = list(map(lambda em: np.asarray(em, dtype='float32'), text_embeddings))
        return text_embeddings

def clip_image_embedding(image_file_url_arr):
    print(f'INFO (clip.py:clip_image_embedding):', image_file_url_arr)
    with torch.no_grad():
        image_arr = _image_file_urls_to_files(image_file_url_arr)
        print(f'INFO (clip.py:clip_image_embedding): image_arr', image_arr)
        processed_image_mappings = ViTL14_336_processor(images=image_arr, return_tensors="pt")
        print(f'INFO (clip.py:clip_image_embedding): processed_image_mappings', processed_image_mappings)
        image_embedding = ViTL14_336_model.get_image_features(**processed_image_mappings)
        # print(f'INFO (clip.py:clip_image_embedding): image_embedding', image_embedding)
        # convert to list of float32 np arrays to be consistent
        image_embeddings = list(map(lambda em: np.asarray(em, dtype='float32'), image_embedding))
        return image_embeddings

# --- text<>image similarity (https://huggingface.co/docs/transformers/model_doc/clip#usage)
def clip_classifications(image_file_urls, classifications, min_similarity=0.1):
    print('INFO (clip.py:clip_classifications)', classifications)
    # PREPROCESS
    # --- image embeddings
    image_files = _image_file_urls_to_files(image_file_urls)
    # --- classifications (actually, it just expects the text as is. no need to tokenize pre-process)
    classification_text = classifications
    # MULTI-MODAL COMPARISON
    alignment = ViTL14_336_processor(text=classification_text, images=image_files, padding=True, return_tensors="pt")
    # input_ids + attention masks =...
    outputs = ViTL14_336_model(**alignment)
    logits_per_image = outputs.logits_per_image
    probabilities = logits_per_image.softmax(dim=1).tolist() # float[][] -> predictionss arr for each image
    # CLASSIFICATIONS
    predictions = []
    # ... for each image
    for image_probs in probabilities:
        image_predicts = []
        for idx, value in enumerate(image_probs):
            # --- expect min of 0.1, otherwise don't push
            if value > min_similarity:
                image_predicts.append({ "classification": classifications[idx], "score": value })
        predictions.append(image_predicts)

    print('INFO (clip.py:clip_classifications) predictions:', predictions)
    return predictions
