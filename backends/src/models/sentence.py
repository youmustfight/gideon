import pydash as _
from sentence_transformers import SentenceTransformer

# Sentence embeddings are more effective + cheaper than GTP3
# https://medium.com/@nils_reimers/openai-gpt-3-text-embeddings-really-a-new-state-of-the-art-in-dense-text-embeddings-6571fe3ec9d9
# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# https://huggingface.co/sentence-transformers/all-mpnet-base-v2
# could try some others: https://www.sbert.net/docs/pretrained_models.html
SENTENCE_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
model = SentenceTransformer(SENTENCE_MODEL_NAME)

def sentence_encode_embeddings(sentences):
    print(f'INFO (sentence.py:sentence_embeddings) start embedding {len(sentences)} sentences') # embeddings
    embeddings = model.encode(sentences, batch_size=20, show_progress_bar=False)
    print(f'INFO (sentence.py:sentence_embeddings) {len(sentences)} sentences = {len(embeddings)} embeddings')
    return embeddings
