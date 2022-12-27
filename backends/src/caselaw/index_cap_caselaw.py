import requests
import sqlalchemy as sa
from dbs.sa_models import CAPCaseLaw
import env
from caselaw.utils.upsert_caselaw import upsert_caselaw
from indexers.utils.extract_document_citing_slavery_summary import extract_document_citing_slavery_summary
from indexers.utils.extract_document_citing_slavery_summary_one_liner import extract_document_citing_slavery_summary_one_liner
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner

async def _index_cap_caselaw_process_content(session, cap_id: int) -> None:
    print(f'INFO (index_cap_caselaw.py): processing cap caselaw #{cap_id} content')
    # --- fetch existing
    query_cap_caselaw = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_caselaw = query_cap_caselaw.scalars().first()
    # --- check if processed
    if cap_caselaw == None or cap_caselaw.status_processing_content != 'completed':
        # --- fetch CAP data
        cap_response = requests.get(
            f'https://api.case.law/v1/cases/{cap_id}/',
            params={
                'full_case': 'true',
            },
            headers={ 'authorization': f'Token {env.env_get_caselaw_access_project()}', 'content-type': 'application/json' },
        )
        cap_response = cap_response.json()
        # --- upsert record (does a session.add)
        cap_case = await upsert_caselaw(session, cap_id, cap_dict=cap_response)
        # --- save status
        cap_case.status_processing_content = 'completed'
        session.add(cap_case) # if modifying a record/model, we can use add() to do an update
    print('INFO (index_cap_caselaw.py:_index_cap_caselaw_process_content): done')


async def _index_cap_caselaw_process_embeddings(session, cap_id: int) -> None:
    # TODO
    # cap_caselaw.status_processing_embeddings = 'completed'
    pass


async def _index_cap_caselaw_process_extractions(session, cap_id: int) -> None:
    print(f'INFO (index_cap_caselaw.py): processing cap caselaw #{cap_id} extractions')
    # --- fetch
    query_cap_caselaw = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_caselaw: CAPCaseLaw = query_cap_caselaw.scalars().first()
    caselaw_content_text = ' '.join(map(lambda content: content['text'], list(cap_caselaw.casebody['opinions'])))
    # --- summaries & extractions
    cap_caselaw.generated_summary = extract_document_summary(caselaw_content_text)
    cap_caselaw.generated_summary_one_liner = extract_document_summary_one_liner(cap_caselaw.generated_summary)
    cap_caselaw.generated_citing_slavery_summary = extract_document_citing_slavery_summary(caselaw_content_text)
    if cap_caselaw.generated_citing_slavery_summary != None:
        cap_caselaw.generated_citing_slavery_summary_one_liner = extract_document_citing_slavery_summary_one_liner(cap_caselaw.generated_citing_slavery_summary)
    # --- save
    cap_caselaw.status_processing_extractions = 'completed'
    session.add(cap_caselaw)


async def index_cap_caselaw(session, cap_id):
    print(f'INFO (index_cap_caselaw.py): indexing cap caselaw #{cap_id}')
    try:
        print(f'INFO (index_cap_caselaw.py): processing cap caselaw #{cap_id} content')
        await _index_cap_caselaw_process_content(session, cap_id)
        print(f'INFO (index_cap_caselaw.py): processing cap caselaw #{cap_id} embeddings')
        await _index_cap_caselaw_process_embeddings(session, cap_id)
        print(f'INFO (index_cap_caselaw.py): processing cap caselaw #{cap_id} extractions')
        # await _index_cap_caselaw_process_extractions(session, cap_id)
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        print(f'INFO (index_cap_caselaw.py): finished intake of caselaw #{cap_id}')
        return cap_id #cap_caselaw_id
    except Exception as err:
        print(f'ERROR (index_cap_caselaw.py):', err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
