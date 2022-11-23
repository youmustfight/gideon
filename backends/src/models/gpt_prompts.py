# SUMMARIZTION
gpt_prompt_summary_concise = """
In the fewest words, summarize of the following passage:

PASSAGE: <<SOURCE_TEXT>>

SUMMARY:
"""

gpt_prompt_summary_detailed = """
Write a detailed summary of the following:

<<SOURCE_TEXT>>

DETAILED SUMMARY:
"""

gpt_prompt_document_type = """
In the fewest words, write what type of document this is called:

<<SOURCE_TEXT>>

TYPE OF DOCUMENT CALLED:
"""

gpt_prompt_video_type = """
In the fewest words, write what type of video content this is:

<<SOURCE_TEXT>>

TYPE OF VIDEO CONTENT:
"""


# EVENTS
gpt_prompt_timeline = """
Write a timeline of events for the following, with one event on each line:

<<SOURCE_TEXT>>

TIMELINE OF EVENTS:
"""

# QA/CONTRASTING
gpt_prompt_answer_question = """
Use only the following passage to give a detailed answer to the question:


QUESTION: <<QUESTION>>


PASSAGE: <<PASSAGE>>


DETAILED ANSWER:
"""

gpt_prompt_contrast_two_statements = """
Using the following two statements by two people, describe only how their positions differ:

STATEMENT by <<USER_ONE>>: <<STATEMENT_ONE>>

STATEMENT by <<USER_TWO>>: <<STATEMENT_TWO>>

DIFFERENCE DESCRIPTION: 
"""

# CITING SLAVERY
gpt_prompt_citing_slavery_summary = """
In the fewest words, summarize the context mentioning slaves in the following passage. If no mention of slavery exists, write '{ESCAPE_PHRASE}':

PASSAGE: <<SOURCE_TEXT>>

SUMMARY:
"""

# EDITING
gpt_prompt_edit_event_timeline = """
Delete any line that does not mention a calendar date.
"""

gpt_prompt_edit_event_timeline_structure = """
Remove bullet points and start each line with the mentioned calendar date as ISO
"""
