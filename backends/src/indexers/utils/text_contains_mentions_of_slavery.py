import re

def text_contains_mentions_of_slavery(text):
  # TODO: get more advanced w/ similarity scores rathern than keyword check
  has_mention = bool(re.search('slave|negro|chattel', text, flags=re.IGNORECASE))
  print(f'INFO (text_contains_mentions_of_slavery.py) has_mention = {has_mention}')
  return has_mention
