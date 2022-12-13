import requests
import sqlalchemy as sa
from dbs.sa_models import CAPCaseLaw
import env
from indexers.utils.extract_document_citing_slavery_summary import extract_document_citing_slavery_summary
from indexers.utils.extract_document_citing_slavery_summary_one_liner import extract_document_citing_slavery_summary_one_liner
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner


async def index_cap_caselaw(session, cap_id):
    print(f"INFO (index_cap_caselaw.py): indexing document #{cap_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} content")
        # --- fetch CAP data
        cap_response = requests.get(
            f'https://api.case.law/v1/cases/{cap_id}/?full_case=true',
            headers={ "authorization": f'Token {env.env_get_caselaw_access_project()}', "content-type": "application/json" },
        )
        cap_response = cap_response.json()
        # --- query for any record of this CAP case in our db already, so we can just update
        query_cap_caselaw = await session.execute(
            sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
        cap_caselaw = query_cap_caselaw.scalars().first()
        # --- upsert TODO: make this less repetative wtf session.add() won't upsert
        if (cap_caselaw != None):
            cap_caselaw.cap_id = cap_response['id']
            cap_caselaw.url = cap_response['url']
            cap_caselaw.name = cap_response['name']
            cap_caselaw.name_abbreviation = cap_response['name_abbreviation']
            cap_caselaw.decision_date = cap_response['decision_date']
            cap_caselaw.docket_number = cap_response['docket_number']
            cap_caselaw.first_page = cap_response['first_page']
            cap_caselaw.last_page = cap_response['last_page']
            cap_caselaw.citations = cap_response['citations']
            cap_caselaw.volume = cap_response['volume']
            cap_caselaw.reporter = cap_response['reporter']
            cap_caselaw.court = cap_response['court']
            cap_caselaw.jurisdiction = cap_response['jurisdiction']
            cap_caselaw.cites_to = cap_response['cites_to']
            cap_caselaw.frontend_url = cap_response['frontend_url']
            cap_caselaw.frontend_pdf_url = cap_response['frontend_pdf_url']
            cap_caselaw.preview = cap_response['preview']
            cap_caselaw.analysis = cap_response['analysis']
            cap_caselaw.last_updated = cap_response['last_updated']
            cap_caselaw.provenance = cap_response['provenance']
            cap_caselaw.casebody = cap_response['casebody']['data']
        else:
            cap_caselaw = CAPCaseLaw(
                cap_id=cap_response['id'],
                url=cap_response['url'],
                name=cap_response['name'],
                name_abbreviation=cap_response['name_abbreviation'],
                decision_date=cap_response['decision_date'],
                docket_number=cap_response['docket_number'],
                first_page=cap_response['first_page'],
                last_page=cap_response['last_page'],
                citations=cap_response['citations'],
                volume=cap_response['volume'],
                reporter=cap_response['reporter'],
                court=cap_response['court'],
                jurisdiction=cap_response['jurisdiction'],
                cites_to=cap_response['cites_to'],
                frontend_url=cap_response['frontend_url'],
                frontend_pdf_url=cap_response['frontend_pdf_url'],
                preview=cap_response['preview'],
                analysis=cap_response['analysis'],
                last_updated=cap_response['last_updated'],
                provenance=cap_response['provenance'],
                casebody=cap_response['casebody']['data'],
            )
        session.add(cap_caselaw)
        
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} embeddings")
        # TODO
        
        print(f"INFO (index_cap_caselaw.py): processing caselaw #{cap_id} extractions")
        caselaw_content_text = " ".join(map(lambda content: content['text'], list(cap_caselaw.casebody['opinions'])))
        cap_caselaw.document_summary = extract_document_summary(caselaw_content_text)
        cap_caselaw.document_summary_one_liner = extract_document_summary_one_liner(cap_caselaw.document_summary)
        cap_caselaw.document_citing_slavery_summary = extract_document_citing_slavery_summary(caselaw_content_text)
        if cap_caselaw.document_citing_slavery_summary != None:
            cap_caselaw.document_citing_slavery_summary_one_liner = extract_document_citing_slavery_summary_one_liner(cap_caselaw.document_citing_slavery_summary)
        session.add(cap_caselaw)

        print(f"INFO (index_cap_caselaw.py): finished intake of caselaw #{cap_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return cap_id #cap_caselaw_id
    except Exception as err:
        print(f"ERROR (index_cap_caselaw.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
