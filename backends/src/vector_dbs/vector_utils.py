import io
import pickle
import numpy

# TENSORS
def write_tensor_to_bytearray(tensor):
    numpy_tensor_array_data = io.BytesIO()
    pickle.dump(tensor, numpy_tensor_array_data)
    numpy_tensor_array_data.seek(0)
    return numpy_tensor_array_data

# TOKENIZING
def tokenize_string(text, strategy):
    # SENTENCES w/ acronym + address safety
    if strategy == "sentence":
        # --- split naively
        splits_init = text.split(". ")
        # --- try to consolidate splits where it may have been on an accronym or address. Ex) ["probable cause, see Fed","R","Crim P","41(c)(1)-(2), at the premises located at 1100 S",...]
        splits_consolidated = []
        for idx, split in enumerate(splits_init):
            if idx == 0 or len(split) > 80: # making 80 to be safe in capturing addresses, legal statute codes
                splits_consolidated.append(split + ".") # add back period
            else:
                splits_consolidated[-1] = splits_consolidated[-1] + f" {split}."
        return splits_consolidated
    # OTHERWISE JUST RETURN TEXT AS ARR
    return [text]

# VECTORS
def similarity(v1, v2):  # return dot product of two vectors
    sim = numpy.dot(v1, v2)
    # print('INFO (numpy): similarity: {sim}'.format(sim=sim))
    return sim
