def serialize_location(location):
    serial = dict(
        document=location.get('document').serialize(),
        document_content=location.get('document_content').serialize(),
        score=location.get('score'))
    if (location.get('image_file') != None):
        serial['image_file'] = location.get('image_file').serialize()
    return serial
