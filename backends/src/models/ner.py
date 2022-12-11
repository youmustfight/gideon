import spacy

# Load transformers trained web model
ner_trf = spacy.load('en_core_web_trf')

# Extract NERs with core TRF model
# Labels: https://spacy.io/models/en#en_core_web_trf-labels
def ner_parse(text, labels):
    results = ner_trf(text)
    # if provided labels, filter via labels
    if labels != None:
        ents = list((filter(lambda e: True if e.label_ in labels else False, results.ents)))
    # otherwise return all entities
    else:
        ents = list(results.ents)
    print("INFO (ner.py:ner_parse): ents", ents)
    return ents

# Extract NERs concerning laws with fine-tuned model
def ner_parse_caselaws(text):
    # TODO: implement fine-tuned model. This is really not working well lol
    return ner_parse(text, ['LAW'])
