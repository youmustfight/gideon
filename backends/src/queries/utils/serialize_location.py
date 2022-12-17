def serialize_location(location):
    serial = dict(
        document=location.get('document').serialize(),
        document_content=location.get('document_content').serialize(),
        score=location.get('score'),
        case_id=location.get('case_id'))
    if (location.get('image_file') != None):
        serial['image_file'] = location.get('image_file').serialize()
    return serial
