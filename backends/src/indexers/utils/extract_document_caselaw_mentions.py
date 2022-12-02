from models.ner import ner_parse_caselaws

async def extract_document_caselaw_mentions(document_text):
    # parse
    entities = ner_parse_caselaws(document_text)
    # deduplicate - exact matches
    caselaw_mentions = set(map(lambda e: e.text, entities))
    # TODO: deduplicate - close matches
    # return
    caselaw_mentions = list(caselaw_mentions)
    print(f'INFO (extract_document_caselaw_mentions): extracting..."', caselaw_mentions)
    return caselaw_mentions
