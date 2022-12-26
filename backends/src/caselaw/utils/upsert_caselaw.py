import sqlalchemy as sa
from dbs.sa_models import CAPCaseLaw

async def upsert_caselaw(session, cap_id, cap_dict) -> CAPCaseLaw:
    print(f'INFO (upsert_caselaw) upsert cap id #{cap_id}')

    # --- query for any record of this CAP case in our db already, so we can just update
    query_cap_caselaw = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_caselaw = query_cap_caselaw.scalars().first()

    # --- upsert TODO: make this less repetative wtf session.add() won't upsert
    if (cap_caselaw != None):
        cap_caselaw.cap_id = cap_dict['id']
        cap_caselaw.url = cap_dict['url']
        cap_caselaw.name = cap_dict['name']
        cap_caselaw.name_abbreviation = cap_dict['name_abbreviation']
        cap_caselaw.decision_date = cap_dict['decision_date']
        cap_caselaw.docket_number = cap_dict['docket_number']
        cap_caselaw.first_page = cap_dict['first_page']
        cap_caselaw.last_page = cap_dict['last_page']
        cap_caselaw.citations = cap_dict['citations']
        cap_caselaw.volume = cap_dict['volume']
        cap_caselaw.reporter = cap_dict['reporter']
        cap_caselaw.court = cap_dict['court']
        cap_caselaw.jurisdiction = cap_dict['jurisdiction']
        cap_caselaw.cites_to = cap_dict['cites_to']
        cap_caselaw.frontend_url = cap_dict['frontend_url']
        cap_caselaw.frontend_pdf_url = cap_dict['frontend_pdf_url']
        cap_caselaw.preview = cap_dict['preview']
        cap_caselaw.analysis = cap_dict['analysis']
        cap_caselaw.last_updated = cap_dict['last_updated']
        cap_caselaw.provenance = cap_dict['provenance']
        cap_caselaw.casebody = cap_dict['casebody']['data']
    else:
        cap_caselaw = CAPCaseLaw(
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
        )

    # --- add to session (commit layer above)
    session.add(cap_caselaw)

    # --- return model in case we want to do follow up mods
    return cap_caselaw
