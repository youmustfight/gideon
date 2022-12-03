from models.ner import ner_parse

async def extract_document_people(document_text):
    # parse
    entities = ner_parse(document_text, ['PERSON'])
    # deduplicate - exact matches
    people = set(map(lambda e: e.text, entities))
    # TODO: deduplicate - close matches
    # return
    people = list(people)
    print(f'INFO (extract_document_people): extracting..."', people)
    return people
