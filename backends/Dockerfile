FROM python:3.10.8-slim
WORKDIR /usr/src/backends

# "wait-for-it.sh" copy + /bin
# https://docs.docker.com/compose/startup-order/
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Install linux packages
RUN apt-get update
RUN apt-get install \
  # --- poppler for pdf -> pngs
  poppler-utils \
  -y

# Cache Transformer/Language Models
# --- spacy: NER (en_core_web_trf)
RUN pip install spacy && python -m spacy download en_core_web_trf
# --- transformers (https://github.com/UKPLab/sentence-transformers/issues/352#issuecomment-923033069)
RUN pip install sentence-transformers transformers
# --- transformers:sentence_transformer
RUN python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")'
# --- transformers:CLIP
RUN python -c 'from transformers import CLIPModel; CLIPModel.from_pretrained("openai/clip-vit-large-patch14-336")'


# Install python packages for app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy src
COPY . .

# Secrets
ARG AWS_REGION
ENV AWS_REGION=$AWS_REGION
ARG AWS_ACCESS_KEY_ID
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ARG TARGET_ENV
ENV TARGET_ENV=$TARGET_ENV
ARG TARGET_SERVICE
ENV TARGET_SERVICE=$TARGET_SERVICE

# Start
EXPOSE 3000
CMD ["python", "-u", "src/start.py"]
 