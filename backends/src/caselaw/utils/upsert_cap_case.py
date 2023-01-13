import datetime
import requests
import sqlalchemy as sa
from dbs.sa_models import CAPCaseLaw
import env

async def _upsert_cap_case(session, cap_id, cap_dict, project_tag) -> CAPCaseLaw:
    print(f'INFO (upsert_cap_case) upsert cap id #{cap_id}')

    # --- query for any record of this CAP case in our db already, so we can just update
    query_cap_case = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_case = query_cap_case.scalars().first()

    # --- upsert TODO: make this less repetative wtf session.add() won't upsert
    if (cap_case != None):
        cap_case.cap_id = cap_dict['id']
        cap_case.url = cap_dict['url']
        cap_case.name = cap_dict['name']
        cap_case.name_abbreviation = cap_dict['name_abbreviation']
        cap_case.decision_date = cap_dict['decision_date']
        cap_case.docket_number = cap_dict['docket_number']
        cap_case.first_page = cap_dict['first_page']
        cap_case.last_page = cap_dict['last_page']
        cap_case.citations = cap_dict['citations']
        cap_case.volume = cap_dict['volume']
        cap_case.reporter = cap_dict['reporter']
        cap_case.court = cap_dict['court']
        cap_case.jurisdiction = cap_dict['jurisdiction']
        cap_case.cites_to = cap_dict['cites_to']
        cap_case.frontend_url = cap_dict['frontend_url']
        cap_case.frontend_pdf_url = cap_dict['frontend_pdf_url']
        cap_case.preview = cap_dict['preview']
        cap_case.analysis = cap_dict['analysis']
        cap_case.last_updated = cap_dict['last_updated']
        cap_case.provenance = cap_dict['provenance']
        cap_case.casebody = cap_dict['casebody']['data']
        cap_case.project_tag = project_tag
        cap_case.created_at = datetime.now()
    else:
        cap_case = CAPCaseLaw(
            cap_id=cap_dict['id'],
            url=cap_dict['url'],
            name=cap_dict['name'],
            name_abbreviation=cap_dict['name_abbreviation'],
            decision_date=cap_dict['decision_date'],
            docket_number=cap_dict['docket_number'],
            first_page=cap_dict['first_page'],
            last_page=cap_dict['last_page'],
            citations=cap_dict['citations'],
            volume=cap_dict['volume'],
            reporter=cap_dict['reporter'],
            court=cap_dict['court'],
            jurisdiction=cap_dict['jurisdiction'],
            cites_to=cap_dict['cites_to'],
            frontend_url=cap_dict['frontend_url'],
            frontend_pdf_url=cap_dict['frontend_pdf_url'],
            preview=cap_dict['preview'],
            analysis=cap_dict['analysis'],
            last_updated=cap_dict['last_updated'],
            provenance=cap_dict['provenance'],
            casebody=cap_dict['casebody']['data'],
            project_tag=project_tag,
        )

    # --- add to session (commit layer above)
    session.add(cap_case)

    # --- return model in case we want to do follow up mods
    return cap_case


async def upsert_cap_case(session, cap_id, project_tag):
    cap_response = requests.get(
        f'https://api.case.law/v1/cases/{cap_id}/',
        params={ 'full_case': 'true' },
        headers={ 'authorization': f'Token {env.env_get_caselaw_access_project()}', 'content-type': 'application/json' },
    )
    cap_response = cap_response.json()
    cap_case = await _upsert_cap_case(session, cap_id, cap_dict=cap_response, project_tag=project_tag)
    # return
    return cap_case
