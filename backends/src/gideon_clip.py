import base64
import io
import clip
from PIL import Image
import torch

# SETUP
# --- vars
CLIP_MODEL = "ViT-L/14@336px" # released April 2022
# --- model + preprocess for images
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load(CLIP_MODEL, device=device)

def clip_vars():
    return {
        "CLIP_MODEL": CLIP_MODEL
    }

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
            # format result
            image_predictions = []
            for value, index in zip(values, indices):
                # --- expect min of 0.01, otherwise don't push
                if value.item() > min_similarity:
                    image_predictions.append({ "classification": classifications[index], "score": value.item() })
            # --- append results
            predictions.append(image_predictions)
    # return
    return predictions

def clip_calc(image_file_paths, classifications, min_similarity):
    print('INFO (CLIP): clip_calc')
    # PREPROCESS
    # --- images
    image_inputs = []
    for im in image_file_paths:
        image_decoded = Image.open(im)
        image_inputs.append(preprocess(image_decoded).unsqueeze(0).to(device))
    # --- classifications, TODO: explore tokenize(f"a photo of {c}")
    classification_inputs = torch.cat([clip.tokenize(f"{c}") for c in classifications]).to(device)
    # MULTI-MODAL COMPARISON
    predictions = clip_predict(image_inputs=image_inputs, classification_inputs=classification_inputs, classifications=classifications, min_similarity=min_similarity)
    print('INFO (CLIP): clip_calc predictions:', predictions)
    return predictions
