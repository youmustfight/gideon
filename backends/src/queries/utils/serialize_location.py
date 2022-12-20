def serialize_location(location):
    # setup
    serial = dict(
        score=location.get('score'),
        case_id=location.get('case_id'))
    # --- if documents exist
    if location.get('document'):
        serial['document'] = location.get('document').serialize()
        serial['document_content'] = location.get('document_content').serialize()
    if location.get('image_file'):
        serial['image_file'] = location.get('image_file').serialize()

    # return 
    return serial
