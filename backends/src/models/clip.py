import clip
from PIL import Image
import requests
import torch

# SETUP
# --- vars
CLIP_MODEL = "ViT-L/14@336px"
# --- model + preprocess for images
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load(CLIP_MODEL, device=device)

def clip_vars():
    return {
        "CLIP_MODEL": CLIP_MODEL
    }

# METHODS
# --- embedding
def clip_text_embedding(text):
    print('INFO (CLIP): clip_text_embedding - {text}'.format(text=text))
    processed_text = clip.tokenize(text).to(device)
    return model.encode_text(processed_text)

def clip_image_embedding(image_file_url):
    print(f'INFO (CLIP): clip_image_embedding - "{image_file_url}"')
    with torch.no_grad():
        image = Image.open(requests.get(image_file_url, stream=True).raw)
        image_input = preprocess(image).unsqueeze(0).to(device) # returns tensor.shape [1,3,244,244]
        image_embedding = model.encode_image(image_input) # returns tensor.shape [1,512]
        return image_embedding


# --- predict method
def clip_predict(image_inputs, classification_inputs, classifications, min_similarity=0.01):
    predictions = []
    # for each image...
    for im in image_inputs:
        with torch.no_grad():
            # --- calculate features
            image_features = model.encode_image(im)
            text_features = model.encode_text(classification_inputs)
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
        image_inputs.append(preprocess(image_decoded).unsqueeze(0).to(device))
    # --- classifications, TODO: explore tokenize(f"a photo of {c}")
    classification_inputs = torch.cat([clip.tokenize(f"{c}") for c in classifications]).to(device)
    # MULTI-MODAL COMPARISON
    predictions = clip_predict(image_inputs=image_inputs, classification_inputs=classification_inputs, classifications=classifications, min_similarity=min_similarity)
    print('INFO (CLIP): clip_classifications predictions:', predictions)
    return predictions
