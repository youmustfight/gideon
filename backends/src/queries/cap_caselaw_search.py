import requests
import env
from caselaw.utils.upsert_caselaw import upsert_caselaw


async def cap_caselaw_search(session, query):
    print('INFO (cap_caselaw_search): query = ', query)
    # Search CAP (w/ full results)
    cap_response = requests.get(
        f'https://api.case.law/v1/cases/',
        params={
            'full_case': 'true',
            'page_size': 10,
            'search': query,
        },
        headers={ "authorization": f'Token {env.env_get_caselaw_access_project()}', "content-type": "application/json" },
    )
    cap_response = cap_response.json()
    cap_results = cap_response['results']
    print('INFO (cap_caselaw_search): cap_response = ', cap_response)

    # Save to Database
    cap_caselaws = []
    for cap_result in cap_results:
        cap_caselaw = await upsert_caselaw(session, cap_id=cap_result['id'], cap_dict=cap_result) 
        cap_caselaws.append(cap_caselaw)

    # Return
    return cap_caselaws