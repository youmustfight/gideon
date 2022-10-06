import base64
import json
import aiofiles
import numpy
import os

dirname = os.path.dirname(__file__)

# MATH
def similarity(v1, v2):  # return dot product of two vectors
    sim = numpy.dot(v1, v2)
    # print('INFO (numpy): similarity: {sim}'.format(sim=sim))
    return sim


# FILES
def get_file_path(relative_path):
    return os.path.join(dirname, relative_path)

def get_documents_json():
    path_to_json = get_file_path("../indexed")
    json_files_paths = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    def json_mapper(json_filename):
        return json.load(open(get_file_path('../indexed/{json_filename}'.format(json_filename=json_filename))))
    return list(map(json_mapper, json_files_paths))

def filter_documents_by_format(formats, documents):
    def filter_by_format(document):
        return document['format'] in formats
    return filter(filter_by_format, documents)

def get_highlights_json():
    path_to_json = get_file_path("../indexed/highlights")
    json_files_paths = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    def json_mapper(json_filename):
        return json.load(open(get_file_path('../indexed/highlights/{json_filename}'.format(json_filename=json_filename))))
    return list(map(json_mapper, json_files_paths))

def open_txt_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def open_img_file_as_base64(filepath):
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string

def write_file(filepath, bytes):
    with open(filepath, 'wb') as file:
        file.write(bytes)

async def async_write_file(path, body):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(body)
    f.close()

# UTILS
def filter_empty_strs(arr):
    return list(filter(None, arr))

def without_keys(d, keys):
    return { x: d[x] for x in d if x not in keys }
