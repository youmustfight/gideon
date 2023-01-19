# MISC/UTIL
 # used spaces instead of _, but gpt completion would make it 'NO MENTION OF SLAVERY'
GPT_NULL_PHRASE = 'NO_MENTION_NULL_PHRASE'

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

gpt_prompt_summary_caselaw_detailed = """
Write a detailed summary of the following case law opinion:

CASE LAW OPINION: <<SOURCE_TEXT>>

DETAILED SUMMARY:
"""

gpt_prompt_summary_one_liner = """
In a single sentence, summarize the following passage.':

PASSAGE: <<SOURCE_TEXT>>

ONE SENTENCE SUMMARY:
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

# TITLES
gpt_prompt_article_title = """
Write an article title given the following set of questions.

QUESTIONS: <<SOURCE_TEXT>>

ARTICLE TITLE: 
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
# V1 - can't remember
# V2 - initial
# V3 - added strictness, "no explicit mention of slaves or slavery occurs".
# V4 - got rid of end sentence: 'If slaves or slavery is not explicitly mentioned, write '{GPT_NULL_PHRASE}
gpt_prompt_citing_slavery_summary = f"""
In the fewest words, summarize the context mentioning slaves in the following case law opinion.

CASE LAW OPINION: <<SOURCE_TEXT>>

SUMMARY:
"""

gpt_prompt_citing_slavery_summary_one_liner = """
In a single sentence, summarize the following passage without excluding any references to slaves or slavery:

PASSAGE: <<SOURCE_TEXT>>

ONE SENTENCE SUMMARY:
"""

# BRIEFS
gpt_prompt_find_facts_for_issue = """
List facts from the passage that relate to the following issue.

ISSUE: <<ISSUE_TEXT>>

PASSAGE: <<SOURCE_TEXT>>

LIST OF RELEVANT FACTS FOR ISSUE:
- 
"""

gpt_prompt_consolidate_facts_for_issue = """
Consolidate facts listed.

FACTS:
<<SOURCE_TEXT>>

CONSOLIDATED FACTS:
- 
"""


# EDITING
gpt_prompt_edit_event_timeline = """
Delete any line that does not mention a calendar date.
"""

gpt_prompt_edit_event_timeline_structure = """
Remove bullet points and start each line with the mentioned calendar date as ISO
"""

gpt_prompt_edit_separate_research_questions_list = """
Separate each research question into a list prefixed with a dash.
"""

gpt_prompt_edit_organize_as_html_markup = """
Organize content in html structure. Exclude markup for head, body, and doctype.
"""
