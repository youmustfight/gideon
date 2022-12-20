from sentence_transformers import SentenceTransformer

# Sentence embeddings are more effective + cheaper than GTP3
# https://medium.com/@nils_reimers/openai-gpt-3-text-embeddings-really-a-new-state-of-the-art-in-dense-text-embeddings-6571fe3ec9d9
# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# https://huggingface.co/sentence-transformers/all-mpnet-base-v2
# could try some others: https://www.sbert.net/docs/pretrained_models.html
SENTENCE_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
model = SentenceTransformer(SENTENCE_MODEL_NAME)

def sentence_encode_embeddings(sentences):
    print('INFO (sentence.py:sentence_embeddings) start', sentences) # embeddings
    embeddings = model.encode(sentences)
    print('INFO (sentence.py:sentence_embeddings) embedded') # embeddings
    return embeddings
