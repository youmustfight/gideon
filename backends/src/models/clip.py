import clip
from PIL import Image
import numpy as np
import requests
import torch

# SETUP
# TODO: this should be dynamic, right now we're locked into 1 version of CLIP
# --- model + preprocess for images
device = "cuda" if torch.cuda.is_available() else "cpu"
ViTL14_336_model, ViTL14_336_preprocess = clip.load("ViT-L/14@336px", device=device)

# METHODS
# --- embedding
def clip_text_embedding(text):
    print('INFO (CLIP): clip_text_embedding - {text}'.format(text=text))
    with torch.no_grad():
        processed_text = clip.tokenize(text).to(device)
        text_embedding = ViTL14_336_model.encode_text(processed_text)
        # convert to list of float32 np arrays to be consistent
        text_embedding = list(map(lambda em: np.asarray(em, dtype='float32'), text_embedding))
        return text_embedding

def clip_image_embedding(image_file_url):
    print(f'INFO (CLIP): clip_image_embedding - "{image_file_url}"')
    with torch.no_grad():
        image = Image.open(requests.get(image_file_url, stream=True).raw)
        image_input = ViTL14_336_preprocess(image).unsqueeze(0).to(device) # returns tensor.shape [1,3,244,244]
        image_embedding = ViTL14_336_model.encode_image(image_input) # returns tensor.shape [1,512]
        image_embedding = image_embedding.tolist()
        # wtf why do i need to [0] getting an extra array level lol
        return list(map(lambda em: np.asarray(em, dtype='float32'), image_embedding))[0]


# --- predict method
def clip_predict(image_inputs, classification_inputs, classifications, min_similarity=0.01):
    predictions = []
    # for each image...
    for im in image_inputs:
        with torch.no_grad():
            # --- calculate features
            image_features = ViTL14_336_model.encode_image(im)
            text_features = ViTL14_336_model.encode_text(classification_inputs)
            # --- pick the top 5 most similar labels for the image
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            values, indices = similarity[0].topk(len(classifications))
            image_predictions = []
            # for each value aka tensor(...)
            for value, index in zip(values, indices):
                # --- expect min of 0.01, otherwise don't push
                if value.item() > min_similarity:
                    image_predictions.append({ "classification": classifications[index], "score": value.item() })
            # --- append results
            predictions.append(image_predictions)
    # return
    return predictions

def clip_classifications(image_file_urls, classifications, min_similarity):
    print('INFO (CLIP): clip_classifications')
    # PREPROCESS
    # --- image embeddings
    image_inputs = []
    for image_file_url in image_file_urls:
        image_decoded = Image.open(requests.get(image_file_url, stream=True).raw)
        image_inputs.append(ViTL14_336_preprocess(image_decoded).unsqueeze(0).to(device))
    # --- classifications, TODO: explore tokenize(f"a photo of {c}")
    classification_inputs = torch.cat([clip.tokenize(f"{c}") for c in classifications]).to(device)
    # MULTI-MODAL COMPARISON
    predictions = clip_predict(image_inputs=image_inputs, classification_inputs=classification_inputs, classifications=classifications, min_similarity=min_similarity)
    print('INFO (CLIP): clip_classifications predictions:', predictions)
    return predictions
