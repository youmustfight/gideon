import requests
import sqlalchemy as sa
from dbs.sa_models import CAPCaseLaw
import env
from caselaw.utils.upsert_caselaw import upsert_caselaw
from indexers.utils.extract_document_citing_slavery_summary import extract_document_citing_slavery_summary
from indexers.utils.extract_document_citing_slavery_summary_one_liner import extract_document_citing_slavery_summary_one_liner
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner


async def index_cap_caselaw(session, cap_id):
    print(f"INFO (index_cap_caselaw.py): indexing document #{cap_id}")
    try:
        # CONTENT
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} content")
        # --- fetch CAP data
        cap_response = requests.get(
            f'https://api.case.law/v1/cases/{cap_id}/?full_case=true',
            headers={ "authorization": f'Token {env.env_get_caselaw_access_project()}', "content-type": "application/json" },
        )
        cap_response = cap_response.json()
        # --- upsert record
        cap_caselaw = await upsert_caselaw(session, cap_id, cap_dict=cap_response)
        
        # EMBEDDINGS
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} embeddings")
        
        # EXTRACTIONS
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} extractions")
        caselaw_content_text = " ".join(map(lambda content: content['text'], list(cap_caselaw.casebody['opinions'])))
        cap_caselaw.generated_summary = extract_document_summary(caselaw_content_text)
        cap_caselaw.generated_summary_one_liner = extract_document_summary_one_liner(cap_caselaw.generated_summary)
        cap_caselaw.generated_citing_slavery_summary = extract_document_citing_slavery_summary(caselaw_content_text)
        if cap_caselaw.generated_citing_slavery_summary != None:
            cap_caselaw.generated_citing_slavery_summary_one_liner = extract_document_citing_slavery_summary_one_liner(cap_caselaw.generated_citing_slavery_summary)
        session.add(cap_caselaw)

        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        print(f"INFO (index_cap_caselaw.py): finished intake of caselaw #{cap_id}")
        return cap_id #cap_caselaw_id
    except Exception as err:
        print(f"ERROR (index_cap_caselaw.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
