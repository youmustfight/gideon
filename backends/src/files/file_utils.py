import base64
import aiofiles
import os

dirname = os.path.dirname(__file__)

# FILES
def get_file_path(relative_path):
    return os.path.join(dirname, relative_path)

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
