FROM python:3.10.8
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

# Install python packages for app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Cache Transformer/Language Models
# --- CLIP (can't get this to work)
# RUN mkdir -p /.cache/clip
# RUN wget -O /.cache/clip/ViT-L-14-336px.pt "https://openaipublic.azureedge.net/clip/models/3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02/ViT-L-14-336px.pt"
# --- spacy: NER (en_core_web_trf)
RUN python -m spacy download en_core_web_trf
# --- transformers (https://github.com/UKPLab/sentence-transformers/issues/352#issuecomment-923033069)
# --- transformers:donut
# --- transformers:sentence_transformer
# RUN python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")'

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

# Start
EXPOSE 3000
CMD ["python", "-u", "src/start.py"]
 