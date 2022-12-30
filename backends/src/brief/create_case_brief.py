import textwrap
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from typing import List
from dbs.sa_models import Brief, Document, DocumentContent
from indexers.utils.tokenize_string import TOKENIZING_STRATEGY
from models.gpt import gpt_completion
from models.gpt_prompts import gpt_prompt_find_facts_for_issue, gpt_prompt_consolidate_facts_for_issue
from indexers.utils.tokenize_string import tokenize_string

async def create_case_brief(session, case_id: int, issues: List[str] = None):
    print('INFO (create_case_brief.py): start', case_id, issues)
    # SETUP
    # --- brief
    brief = Brief(case_id=case_id)
    # --- all case documents text TODO: need a way to do citations
    documents_query = await session.execute(
        sa.select(Document)
            .join(Document.content)
            .options(joinedload(Document.content))
            .where(Document.case_id == case_id)
            .where(DocumentContent.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value)
    )
    documents = documents_query.scalars().unique().all()
    def map_document_text(doc):
        document_content_text_arr = list(map(lambda dc: dc.text, doc.content))
        document_content_text_arr = list(filter(lambda str: str != None, document_content_text_arr))
        return " ".join(document_content_text_arr)
    documents_text_arr = list(map(map_document_text, documents))

    # ISSUE
    # --- pull from inputs
    brief.issues = issues
    print('INFO (create_case_brief.py): brief.issues', brief.issues)
    
    # FACTS
    brief.facts = []
    # ... for each issue, find/compile relevant facts
    for issue in brief.issues:
        print('INFO (create_case_brief.py): issue', issue)
        issue_facts_str = ""
        # ... for each document
        for document_text in documents_text_arr:
            # --- walk across all documents text chunks
            chunks = tokenize_string(document_text, TOKENIZING_STRATEGY.gpt.value, 3000) # 4k max for davinci, 2k for curie
            print('INFO (create_case_brief.py): # of document_text chunks', len(chunks))
            for chunk in chunks:
                # 4264 token max
                issue_facts_for_text_chunk = gpt_completion(
                    gpt_prompt_find_facts_for_issue.replace('<<ISSUE_TEXT>>', issue['issue']).replace('<<SOURCE_TEXT>>', chunk),
                    max_tokens=400)
                issue_facts_str += issue_facts_for_text_chunk
                issue_facts_str += '\n'
        print('INFO (create_case_brief.py): issue_facts_str\n', issue_facts_str)

        # --- edit/consolidate (can be more than 4k tokens, so need to break down again)
        # v1
        # edited_issue_facts_str = ""
        # issue_facts_chunks = tokenize_string(issue_facts_str, TOKENIZING_STRATEGY.gpt.value, 2000)
        # for issue_facts_chunk in issue_facts_chunks:
        #     issue_facts_chunk_str = gpt_completion(
        #         gpt_prompt_consolidate_facts_for_issue.replace('<<SOURCE_TEXT>>', issue_facts_chunk),
        #         max_tokens=500)
        #     edited_issue_facts_str += issue_facts_chunk_str
        #     edited_issue_facts_str += '\n'
        # print('INFO (create_case_brief.py): issue_facts_str consolidated/edited\n', issue_facts_str)
        # v2
        # similarity score to group facts, then we can summarize/collapse clusters of repeated points into a single list item

        # --- split on '-' and push to facts array
        brief.facts += list(map(lambda fact: dict(text=fact.strip()), issue_facts_str.split('\n-')))

    # RETURN
    print('INFO (create_case_brief.py): finished', case_id, issues)
    return brief
