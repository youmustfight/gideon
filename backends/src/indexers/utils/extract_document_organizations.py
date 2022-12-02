from models.ner import ner_parse

async def extract_document_organizations(document_text):
    # parse
    entities = ner_parse(document_text, ['ORG'])
    # deduplicate - exact matches
    organizations = set(map(lambda e: e.text, entities))
    # TODO: deduplicate - close matches
    # return
    organizations = list(organizations)
    print(f'INFO (extract_document_organizations): extracting names..."', organizations)
    return organizations
