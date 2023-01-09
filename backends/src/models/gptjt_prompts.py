import datetime


# tested out w/ https://huggingface.co/spaces/togethercomputer/GPT-JT
gptjt_prompt_date_iso_edit = f"""
The current year is {datetime.date.today().year}. Edit the date into the ISO format.

Input: SEPT 9
Output: {datetime.date.today().year}-09-09

Input: FEBRURARY 17 2022
Output: 2022-02-17

Input: July 24, 1990
Output: 1990-07-24

Input: dec 13
Output: {datetime.date.today().year}-12-13

Input: ja n ur ary 21, 1887
Output: 1887-01-21

Input: <<SOURCE_TEXT>>
Output:
"""