from enum import Enum
import pydash as _
import textwrap

class TOKENIZING_STRATEGY(Enum):
    gpt = "gpt"
    word = "word"
    sentence = "sentence"
    sentences_20 = "sentences_20"
    max_size = "max_size"

TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH = 80 # fyi, tried 40 but was too short. Better to err longer than split sentences

# HELPERS
# --- sentences
def split_text_sentences(text):
    # --- split naively
    splits_init = text.split(". ")
    # --- try to consolidate splits where it may have been on an accronym or address. Ex) ["probable cause, see Fed","R","Crim P","41(c)(1)-(2), at the premises located at 1100 S",...]
    splits_consolidated = []
    for idx, split in enumerate(splits_init):
        if idx == 0 or len(split) > TOKENIZING_STRING_SENTENCE_SPLIT_MIN_LENGTH:
            splits_consolidated.append(split + ".") # add back period
        else:
            splits_consolidated[-1] = splits_consolidated[-1] + f" {split}."
    return splits_consolidated
# --- words
def split_text_words(text):
    # TODO: make better
    return text.split(' ')
# --- gpt
def split_text_gpt(text):
    # TODO: make better. rough shot but puncutation affects this (https://beta.openai.com/tokenizer)
    return textwrap.wrap(text, 3, drop_whitespace=False)

# TOKENIZING
def tokenize_string(text, strategy, token_count=None):
    # --- sentences w/ acronym + address safety
    if strategy == TOKENIZING_STRATEGY.sentence.value and token_count == None:
        sentences = split_text_sentences(text)
        return sentences
    if strategy == TOKENIZING_STRATEGY.sentence.value and token_count != None:
        sentences = split_text_sentences(text)
        sentences_chunks_by_count = _.chunk(sentences, token_count) # could change this in the future maybe
        return list(map(lambda sentences: " ".join(sentences)), sentences_chunks_by_count)
    if strategy == TOKENIZING_STRATEGY.sentences_20.value:
        sentences = split_text_sentences(text)
        sentences_chunks_by_20 = _.chunk(sentences, 20) # could change this in the future maybe
        return list(map(lambda sentences: " ".join(sentences)), sentences_chunks_by_20)

    # --- words
    if strategy == TOKENIZING_STRATEGY.word.value and token_count != None:
        words = split_text_words(text)
        words_chunks_by_count = _.chunk(words, token_count) # could change this in the future maybe
        return list(map(lambda words: " ".join(words), words_chunks_by_count))

    # --- gpt
    if strategy == TOKENIZING_STRATEGY.gpt.value and token_count != None:
        words = split_text_gpt(text)
        words_chunks_by_count = _.chunk(words, token_count) # could change this in the future maybe
        return list(map(lambda words: "".join(words), words_chunks_by_count))

    # --- DEPRECATE max sizes (max_size depends on encoding model + token count is word based, not char length based)
    if strategy == TOKENIZING_STRATEGY.max_size.value:
        return textwrap.wrap(text, 3_500)

    # --- no strategy
    return [text]
