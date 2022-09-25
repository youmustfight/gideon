import os

dirname = os.path.dirname(__file__)

def filter_empty_strs(arr):
    return list(filter(None, arr))

def get_file_path(relative_path):
    return os.path.join(dirname, relative_path)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
