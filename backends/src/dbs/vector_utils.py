import io
import pickle
import numpy

from files.s3_utils import s3_upload_file_bytes

# TENSORS
def write_tensor_to_bytearray(tensor):
    numpy_tensor_array_data = io.BytesIO()
    pickle.dump(tensor, numpy_tensor_array_data)
    numpy_tensor_array_data.seek(0)
    return numpy_tensor_array_data

def backup_tensor_to_s3(embedding_id, tensor):
    numpy_tensor_bytearray = write_tensor_to_bytearray(tensor)
    npy_file_key = f"embeddings/embedding_{embedding_id}.npy"
    s3_upload_file_bytes(npy_file_key, numpy_tensor_bytearray)

# VECTORS
def similarity(v1, v2):  # return dot product of two vectors
    sim = numpy.dot(v1, v2)
    # print('INFO (numpy): similarity: {sim}'.format(sim=sim))
    return sim
