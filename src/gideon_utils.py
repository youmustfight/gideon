import json
import numpy
import os

dirname = os.path.dirname(__file__)

# MATH
def similarity(v1, v2):  # return dot product of two vectors
    sim = numpy.dot(v1, v2)
    print('INFO (numpy): similarity: {sim}'.format(sim=sim))
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

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


# UTILS
def filter_empty_strs(arr):
    return list(filter(None, arr))

def without_keys(d, keys):
    return { x: d[x] for x in d if x not in keys }
