import pydash as _
import sqlalchemy as sa
from ai.agents.ai_action_agent import AI_ACTIONS, create_ai_action_agent, get_global_ai_action_locks
from dbs.sa_models import CAPCaseLaw, CAPCaseLawContent, Embedding
from indexers.utils.extract_document_citing_slavery_summary import extract_document_citing_slavery_summary
from indexers.utils.extract_document_citing_slavery_summary_one_liner import extract_document_citing_slavery_summary_one_liner
from indexers.utils.text_contains_mentions_of_slavery import text_contains_mentions_of_slavery
from indexers.utils.tokenize_string import safe_string

async def _index_cap_case_process_content(session, cap_id: int) -> None:
    print(f'INFO (index_cap_case.py): processing cap caselaw #{cap_id} content')
    # 1. CHECK EXISTING
    query_cap_case = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_case = query_cap_case.scalars().first()
    # --- check if processed
    if cap_case.status_processing_content != 'completed':
        # 2. UPSERT CASELAW CONTENT
        cap_case_content_models = []
        # --- head_matter
        cap_case_content_models.append(CAPCaseLawContent(
            cap_case_id=cap_case.id,
            type="head_matter",
            text=safe_string(cap_case.casebody.get('head_matter')),
        ))
        # --- opinion paragraphs: majority
        opinion_majority_text = _.find(cap_case.casebody['opinions'], lambda o: o['type'] == 'majority')['text']
        opinion_majority_text_paragraphs = safe_string(opinion_majority_text).split('\n')
        for idx, opinion_majority_text_paragraph in enumerate(opinion_majority_text_paragraphs):
            cap_case_content_models.append(CAPCaseLawContent(
                cap_case_id=cap_case.id,
                type="opinion_majority_paragraph",
                text=safe_string(opinion_majority_text_paragraph),
                paragraph_number=(idx + 1),
            ))
        session.add_all(cap_case_content_models)
        # SAVE
        cap_case.status_processing_content = 'completed'
        session.add(cap_case) # if modifying a record/model, we can use add() to do an update
    print('INFO (index_cap_case.py:_index_cap_case_process_content): done')


async def _index_cap_case_process_embeddings(session, cap_id: int) -> None:
    # FETCH
    query_cap_case = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_case: CAPCaseLaw = query_cap_case.scalars().first()
    ai_action_locks = await get_global_ai_action_locks(session)
    # EMBED
    if cap_case.status_processing_embeddings != 'completed':
        # --- head_matter
        aiagent_cap_case_head_matter_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.cap_case_head_matter_similarity_text_embed, ai_action_locks=ai_action_locks)
        cap_case_head_matter_content_query = await session.execute(sa.select(CAPCaseLawContent).where(
            sa.and_(CAPCaseLawContent.cap_case_id == cap_case.id, CAPCaseLawContent.type == "head_matter")
        ))
        cap_case_content_head_matter = cap_case_head_matter_content_query.scalars().first()
        head_matter_text = cap_case_content_head_matter.text
        # --- head_matter: process
        if head_matter_text != None and len(head_matter_text) > 0:
            head_matter_text_embeddings = aiagent_cap_case_head_matter_embeder.encode_text([head_matter_text])
            head_matter_text_embeddings_as_models = []
            for embedding in head_matter_text_embeddings:
                head_matter_text_embeddings_as_models.append(Embedding(
                    cap_case_id=cap_case.id,
                    cap_case_content_id=cap_case_content_head_matter.id,
                    encoded_model_engine=aiagent_cap_case_head_matter_embeder.model_name,
                    encoding_strategy="text",
                    vector_dimensions=len(embedding),
                    vector_json=embedding.tolist(), # converts ndarry -> list (but also makes serializable data)
                    ai_action=aiagent_cap_case_head_matter_embeder.ai_action.value,
                    index_id=aiagent_cap_case_head_matter_embeder.index_id,
                    index_partition_id=aiagent_cap_case_head_matter_embeder.index_partition_id,
                    indexed_status='queued'
                ))
            session.add_all(head_matter_text_embeddings_as_models)
        # --- paragraphs/sections    
        aiagent_cap_case_opinion_paragraph_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.cap_case_opinion_paragraph_similarity_text_embed, ai_action_locks=ai_action_locks)
        cap_case_majority_paragraphs_content_query = await session.execute(sa.select(CAPCaseLawContent).where(
            sa.and_(CAPCaseLawContent.cap_case_id == cap_case.id, CAPCaseLawContent.type == "opinion_majority_paragraph")
        ))
        cap_case_paragraphs = cap_case_majority_paragraphs_content_query.scalars().all()
        cap_case_paragraphs_text_list = list(map(lambda e: e.text, cap_case_paragraphs))
        print('cap_case_paragraphs_text_list', cap_case_paragraphs_text_list)
        cap_case_paragraphs_embeddings = aiagent_cap_case_opinion_paragraph_embeder.encode_text(cap_case_paragraphs_text_list)
        # --- paragraphs/sections: process
        if len(cap_case_paragraphs) > 0:
            opinion_paragraphs_text_embedding_as_models = []
            for idx, cap_case_paragraph in enumerate(cap_case_paragraphs):
                opinion_paragraphs_text_embedding_as_models.append(Embedding(
                    cap_case_id=cap_case.id,
                    cap_case_content_id=cap_case_paragraph.id,
                    encoded_model_engine=aiagent_cap_case_opinion_paragraph_embeder.model_name,
                    encoding_strategy="text",
                    vector_dimensions=len(cap_case_paragraphs_embeddings[idx]),
                    vector_json=cap_case_paragraphs_embeddings[idx].tolist(), # converts ndarry -> list (but also makes serializable data)
                    ai_action=aiagent_cap_case_opinion_paragraph_embeder.ai_action.value,
                    index_id=aiagent_cap_case_opinion_paragraph_embeder.index_id,
                    index_partition_id=aiagent_cap_case_opinion_paragraph_embeder.index_partition_id,
                    indexed_status='queued'
                ))
            session.add_all(opinion_paragraphs_text_embedding_as_models)
        # SAVE
        cap_case.status_processing_embeddings = "completed"
        session.add(cap_case)
    print('INFO (index_cap_case.py:_index_cap_case_process_embeddings): done')


async def _index_cap_case_process_extractions(session, cap_id: int) -> None:
    print(f'INFO (index_cap_case.py): processing cap caselaw #{cap_id} extractions')
    # FETCH
    query_cap_caselaw = await session.execute(
        sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
    cap_caselaw: CAPCaseLaw = query_cap_caselaw.scalars().first()
    # EXTRACT
    if cap_caselaw.status_processing_extractions != 'completed':
        caselaw_content_text = ' '.join(map(lambda content: content['text'], list(cap_caselaw.casebody['opinions'])))
        # --- summaries & extractions TODO: not doing this to save $. utilize cap case "head_matter"
        # if cap_caselaw.generated_summary == None:
        #     cap_caselaw.generated_summary = extract_text_summary(caselaw_content_text, use_prompt=gpt_prompt_summary_caselaw_detailed)
        #     cap_caselaw.generated_summary_one_liner = extract_document_summary_one_liner(cap_caselaw.generated_summary)
        # --- summaries & extractions (citing slavery)
        if text_contains_mentions_of_slavery(caselaw_content_text) == True:
            cap_caselaw.generated_citing_slavery_summary = extract_document_citing_slavery_summary(caselaw_content_text)
            cap_caselaw.generated_citing_slavery_summary_one_liner = extract_document_citing_slavery_summary_one_liner(cap_caselaw.generated_citing_slavery_summary)
        else:
            cap_caselaw.generated_citing_slavery_summary = None
            cap_caselaw.generated_citing_slavery_summary_one_liner = None
        # --- save
        cap_caselaw.status_processing_extractions = 'completed'
        session.add(cap_caselaw)
    print('INFO (index_cap_case.py:_index_cap_case_process_embeddings): done')


async def index_cap_case(session, cap_id):
    print(f'INFO (index_cap_case.py): indexing cap caselaw #{cap_id}')
    try:
        print(f'INFO (index_cap_case.py): processing cap caselaw #{cap_id} content')
        await _index_cap_case_process_content(session, cap_id)
        print(f'INFO (index_cap_case.py): processing cap caselaw #{cap_id} embeddings')
        await _index_cap_case_process_embeddings(session, cap_id)
        print(f'INFO (index_cap_case.py): processing cap caselaw #{cap_id} extractions')
        await _index_cap_case_process_extractions(session, cap_id)
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        print(f'INFO (index_cap_case.py): finished intake of caselaw #{cap_id}')
        return cap_id #cap_caselaw_id
    except Exception as err:
        print(f'ERROR (index_cap_case.py):', err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
