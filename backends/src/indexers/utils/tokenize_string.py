from enum import Enum
import pydash as _
import textwrap

class TOKENIZING_STRATEGY(Enum):
    sentence = "sentence"
    sentences_20 = "sentences_20"
    max_size = "max_size"

TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH = 40

# TOKENIZING
def tokenize_string(text, strategy):
    # HELPERS
    def split_text_sentences(text):
        # --- split naively
        splits_init = text.split(". ")
        # --- try to consolidate splits where it may have been on an accronym or address. Ex) ["probable cause, see Fed","R","Crim P","41(c)(1)-(2), at the premises located at 1100 S",...]
        splits_consolidated = []
        for idx, split in enumerate(splits_init):
            if idx == 0 or len(split) > TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH: # making 40 to be safe in capturing addresses, legal statute codes
                splits_consolidated.append(split + ".") # add back period
            else:
                splits_consolidated[-1] = splits_consolidated[-1] + f" {split}."
        return splits_consolidated
    # PROCESS
    # --- sentences w/ acronym + address safety
    if strategy == TOKENIZING_STRATEGY.sentence.value:
        sentences = split_text_sentences(text)
        return sentences
    if strategy == TOKENIZING_STRATEGY.sentences_20.value:
        sentences = split_text_sentences(text)
        sentences_chunks_by_20 = _.chunk(sentences, 20) # could change this in the future maybe
        return list(map(lambda sentences: " ".join(sentences)), sentences_chunks_by_20)
    # --- max sizes
    if strategy == TOKENIZING_STRATEGY.max_size.value:
        return textwrap.wrap(text, 3_500)
    # --- the text w/o a strategy
    return [text]