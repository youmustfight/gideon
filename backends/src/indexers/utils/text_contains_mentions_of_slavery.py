import re

def text_contains_mentions_of_slavery(text):
  # TODO: get more advanced w/ similarity scores rathern than keyword check
  return bool(re.search('slave|negro|chattel', text, flags=re.IGNORECASE))
