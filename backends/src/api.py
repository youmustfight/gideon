from contextvars import ContextVar
from datetime import datetime
from htmldocx import HtmlToDocx
from typing import List
from sanic import response, Sanic
from sanic.response import json
from sanic_cors import CORS
import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload, subqueryload

from ai.agents.ai_action_agent import generate_ai_action_locks
from auth.auth_route import auth_route
from auth.token import decode_token, encode_token
from caselaw.deindex_cap_case import deindex_cap_case
from caselaw.index_cap_case import _index_cap_case_process_extractions
from caselaw.utils.upsert_cap_case import upsert_cap_case
from dbs.sa_models import serialize_list, AIActionLock, Case, CAPCaseLaw, Brief, Document, DocumentContent, File, Organization, Writing, User
from dbs.sa_sessions import create_sqlalchemy_session
import env
from indexers.deindex_document import deindex_document
from indexers.deindex_writing import deindex_writing
from indexers.utils.index_document_prep import index_document_prep
from indexers.utils.extract_document_summary import extract_document_summary
from ai.requests.cap_caselaw_search import cap_caselaw_search
from ai.requests.brief_fact_similarity import brief_fact_similarity
from ai.requests.question_answer import question_answer
from ai.requests.search_locations import search_locations
from ai.requests.writing_similarity import writing_similarity
from ai.requests.utils.serialize_location import serialize_location
from ai.requests.write_memo_for_document import write_memo_for_document
from ai.requests.write_template_with_ai import write_template_with_ai
from arq_queue.create_queue_pool import create_queue_pool

# INIT
api_app = Sanic('api')
api_app.config['RESPONSE_TIMEOUT'] = 60 * 30 # HACK: until we move pdf processing outside the api endpoints, disallowing 503 timeout responses now


# MIDDLEWARE
# --- cors
CORS(api_app)
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
_base_model_session_ctx = ContextVar('session')
@api_app.middleware('request')
async def inject_session(request):
    request.ctx.session = create_sqlalchemy_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@api_app.middleware('response')
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()

    
# AUTH
@api_app.route('/v1/auth/login', methods = ['POST'])
async def app_route_auth_login(request):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(
            sa.select(User)
                .options(selectinload(User.cases), selectinload(User.organizations))
                .where(User.email == request.json["email"])
        )
        user = query_user.scalar_one_or_none()
        if (user != None and request.json.get('password') == user.password):
            token = encode_token({ 'issued_at': datetime.now().timestamp(), 'user_id': user.id })
            return json({ 'status': 'success',  'token': token, 'user': user.serialize() })
        else:
            return json({
                'status': 'error',
                'message': 'No user found.' if user == None else 'Bad password.',
            }, status=400)

@api_app.route('/v1/auth/user', methods = ['GET'])
async def app_route_auth_user(request):
    session = request.ctx.session 
    async with session.begin():
        if (request.token != None):
            token_payload = decode_token(request.token)
            query_user = await session.execute(
                sa.select(User).where(User.id == int(token_payload['user_id'])))
            user = query_user.scalar_one_or_none()
            if (user != None):
                return json({ 'status': 'success',  'user': user.serialize() })
        else:
            return json({ 'status': 'success', 'user': None })


# AI ACTIONS/QUERIES
@api_app.route('/v1/ai/fill-writing-template', methods = ['POST'])
@auth_route
async def app_route_ai_fill_writing_template(request):
    session = request.ctx.session
    async with session.begin():
        # setup writing model
        writing_model = Writing(
            case_id=request.json.get('writing').get('case_id'),
            is_template=request.json.get('writing').get('is_template'),
            name=request.json.get('writing').get('name'),
            organization_id=request.json.get('writing').get('organization_id'),
            forked_writing_id=int(request.json.get('writing').get('forked_writing_id')) if request.json.get('writing').get('forked_writing_id') != None else None,
        )
        # pass it to ai writer
        updated_writing_model = await write_template_with_ai(session, writing_model, request.json.get('prompt_text'))
        # save
        session.add(updated_writing_model)
    # send back data to frontend
    session.refresh(updated_writing_model)
    return json({ 'status': 'success', 'data': { 'writing': updated_writing_model.serialize() } })

@api_app.route('/v1/ai/write-memo-for-document', methods = ['POST'])
@auth_route
async def app_route_ai_write_document_memo(request):
    session = request.ctx.session
    async with session.begin():
        writing_model = await write_memo_for_document(
            session,
            document_id=int(request.json.get('document_id')),
            prompt_text=request.json.get('prompt_text'),
            user_id=int(request.json.get('user_id')))
        # save
        session.add(writing_model)
    # send back data to frontend
    await session.refresh(writing_model)
    return json({ 'status': 'success', 'data': { 'writing': writing_model.serialize() } })

@api_app.route('/v1/ai/query-document-answer', methods = ['POST'])
@auth_route
async def app_route_ai_query_document_answer(request):
    session = request.ctx.session
    async with session.begin():
        case_id = request.json.get('case_id')
        document_id = request.json.get('document_id')
        user_id = request.json.get('user_id')
        answer, locations = await question_answer(
            session,
            query_text=request.json.get('query'),
            case_id=int(case_id) if case_id != None else None,
            document_id=int(document_id) if document_id != None else None,
            user_id=int(user_id) if user_id != None else None)
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'answer': answer, 'locations': locations } })

@api_app.route('/v1/ai/query-document-locations', methods = ['POST'])
@auth_route
async def app_route_ai_query_document_locations(request):
    session = request.ctx.session
    async with session.begin():
        # Fetch
        case_id = request.json.get('case_id')
        document_id = request.json.get('document_id')
        user_id = request.json.get('user_id')
        locations = await search_locations(
            session,
            query_text=request.json.get('query'),
            case_id=int(case_id) if case_id != None else None,
            document_id=int(document_id) if document_id != None else None,
            user_id=int(user_id) if user_id != None else None)
        # Serialize (TODO): make 'Location' class rather than plain dict
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'locations': locations } })

@api_app.route('/v1/ai/query-brief-fact-similiarty', methods = ['POST'])
@auth_route
async def app_route_ai_query_brief_fact_similarity(request):
    session = request.ctx.session
    async with session.begin():
        # Fetch
        case_id = request.json.get('case_id')
        organization_id = request.json.get('organization_id')
        query_text = request.json.get('query')
        locations = await brief_fact_similarity(
            session,
            case_id=int(case_id) if case_id != None else None,
            organization_id=int(organization_id),
            query_text=query_text)
        # Serialize (TODO): make 'Location' class rather than plain dict
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'locations': locations } })

@api_app.route('/v1/ai/query-writing-similarity', methods = ['POST'])
@auth_route
async def app_route_ai_query_writing_similarity(request):
    session = request.ctx.session
    async with session.begin():
        # Fetch
        organization_id = request.json.get('organization_id')
        locations = await writing_similarity(
            session,
            organization_id=int(organization_id),
            query=request.json.get('query'))
        # Serialize (TODO): make 'Location' class rather than plain dict
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'locations': locations } })

@api_app.route('/v1/ai/summarize', methods = ['POST'])
@auth_route
async def app_route_ai_summarize(request):
    session = request.ctx.session
    async with session.begin():
        # TODO: save request query + results
        # Summarize
        summary = extract_document_summary(request.json.get('text'))
    return json({ 'status': 'success', 'data': { 'summary': summary } })


# AI ACTION LOCK
@api_app.route('/v1/ai_action_locks', methods = ['POST'])
@auth_route
async def app_route_ai_action_locks_post(request):
    session = request.ctx.session
    async with session.begin():
        # --- check for existing action locks
        query_locks = await session.execute(sa.select(AIActionLock).where(sa.and_(
            AIActionLock.case_id.is_(None),
            AIActionLock.organization_id.is_(None),
            AIActionLock.user_id.is_(None),
        )))
        locks = query_locks.scalars().all()
        # --- if no global locks exist, add new action locks
        if len(locks) == 0:
            session.add_all(generate_ai_action_locks())
    return json({ 'status': 'success' })


# CASES
@api_app.route('/v1/cases', methods = ['GET'])
@auth_route
async def app_route_cases(request):
    session = request.ctx.session
    async with session.begin():
        cases_json = []
        query_cases = await session.execute(
            sa.select(Case)
                .options(
                    joinedload(Case.users),
                    joinedload(Case.brief),
                )
                .where(Case.organization_id == int(request.args.get('organization_id')))
        )
        cases = query_cases.scalars().unique().all()
        cases_json = serialize_list(cases, ['brief', 'users'])
    return json({ 'status': 'success', 'data': { 'cases': cases_json } })

@api_app.route('/v1/case/<case_id>', methods = ['GET'])
@auth_route
async def app_route_case_get(request, case_id):
    session = request.ctx.session
    async with session.begin():
        query_case = await session.execute(
            sa.select(Case)
                .options(
                    joinedload(Case.users),
                    joinedload(Case.brief),
                )
                .where(Case.id == int(case_id))
        )
        case = query_case.scalars().unique().one()
        case_json = case.serialize(['brief', 'users'])
    return json({ 'status': 'success', 'data': { 'case': case_json } })
    

@api_app.route('/v1/case/<case_id>', methods = ['PUT'])
@auth_route
async def app_route_case_put(request, case_id):
    session = request.ctx.session
    async with session.begin():
        query_case = await session.execute(
            sa.select(Case).where(Case.id == int(case_id)))
        case = query_case.scalars().one()
        # TODO: make better lol
        case.name = request.json['case']['name']
        session.add(case)
    return json({ 'status': 'success' })

@api_app.route('/v1/case/<case_id>/ai_action_locks_reset', methods = ['PUT'])
@auth_route
async def app_route_case_put_action_locks(request, case_id):
    session = request.ctx.session
    async with session.begin():
        case_id = int(case_id)
        # --- delete existing action locks
        await session.execute(sa.delete(AIActionLock).where(AIActionLock.case_id == case_id))
        # --- add new action locks
        session.add_all(generate_ai_action_locks(case_id))
    return json({ 'status': 'success' })

@api_app.route('/v1/case/<case_id>/reindex_all_documents', methods = ['PUT'])
@auth_route
async def app_route_case_put_reprocess_all_data(request, case_id):
    session = request.ctx.session
    async with session.begin():
        case_id = int(case_id)
        query_documents = await session.execute(sa.select(Document).where(Document.case_id == case_id))
        documents: List[Document] = query_documents.scalars().all()
        # --- for each document, delete embeddings, document content, remove from vector dbs/indexes
        for document in documents:
            await deindex_document(session, document.id)
    # --- for each document, re-run document processing + embedding + vector db/index upsertion
    arq_pool = await create_queue_pool()
    for document in documents:
        if document.type == 'audio':
            await arq_pool.enqueue_job('job_index_document_audio', document.id)
        if document.type == 'docx':
            await arq_pool.enqueue_job('job_index_document_docx', document.id)
        if document.type == 'image':
            await arq_pool.enqueue_job('job_index_document_image', document.id)
        if document.type == 'pdf':
            await arq_pool.enqueue_job('job_index_document_pdf', document.id)
        if document.type == 'video':
            await arq_pool.enqueue_job('job_index_document_video', document.id)
    return json({ 'status': 'success' })

@api_app.route('/v1/case', methods = ['POST'])
@auth_route
async def app_route_case_post(request):
    session = request.ctx.session
    async with session.begin():
        # --- get user for relation
        query_user = await session.execute(sa.select(User).where(User.id == int(request.json['user_id'])))
        user = query_user.scalars().one()
        # --- insert case w/ user (model mapping/definition knows how to insert w/ junction table)
        case_to_insert = Case(
            ai_action_locks=generate_ai_action_locks(),
            created_at=datetime.now(),
            name=request.json['name'],
            organization_id=request.json['organization_id'],
            users=[user]
        )
        session.add(case_to_insert)
    return json({ 'status': 'success', 'data': { "case": { "id": case_to_insert.id } } })

@api_app.route('/v1/case/<case_id>/brief', methods = ['GET'])
@auth_route
async def app_route_case_brief_get(request, case_id):
    session = request.ctx.session
    async with session.begin():
        query_brief = await session.execute(
            sa.select(Brief).where(Brief.case_id == int(case_id)))
        brief = query_brief.scalar_one_or_none()
        return json({ 'status': 'success', 'data': { 'brief': None if brief == None else brief.serialize() } })

@api_app.route('/v1/case/<case_id>/brief', methods = ['POST'])
@auth_route
async def app_route_case_brief_post(request, case_id):
    arq_pool = await create_queue_pool()
    arq_job = await arq_pool.enqueue_job('job_create_case_brief', case_id=int(case_id), issues=request.json.get('issues'))
    return json({ 'status': 'success' })

@api_app.route('/v1/case/<case_id>/user', methods = ['POST'])
@auth_route
async def app_route_case_user(request, case_id):
    session = request.ctx.session
    action = request.json.get('action')
    query_case = await session.execute(
        sa.select(Case)
            .options(joinedload(Case.users))
            .where(Case.id == int(case_id)))
    case = query_case.scalars().unique().one()
    user_id = request.json.get('user_id')
    query_user = await session.execute(sa.select(User).where(User.id == int(user_id)))
    user = query_user.scalars().one()
    # --- if adding
    if action == 'add':
        case.users.append(user)
        session.add(case)
    # --- if removing
    elif action == 'remove':
        case.users.remove(user)
        session.add(case)
    # --- save
    await session.commit()
    return json({ 'status': 'success' })


# BRIEFS
@api_app.route('/v1/brief/<brief_id>', methods = ['GET'])
@auth_route
async def app_route_brief_get(request, brief_id):
    session = request.ctx.session
    async with session.begin():
        query_brief = await session.execute(
            sa.select(Brief).where(Brief.id == int(brief_id)))
        brief = query_brief.scalar_one_or_none()
        brief_json = brief.serialize()
    return json({ 'status': 'success', "brief": brief_json })

@api_app.route('/v1/brief/<brief_id>', methods = ['PUT'])
@auth_route
async def app_route_brief_put(request, brief_id):
    session = request.ctx.session
    async with session.begin():
        query_brief = await session.execute(
            sa.select(Brief).where(Brief.id == int(brief_id)))
        brief = query_brief.scalars().one()
        # --- facts
        if (request.json.get('brief').get('facts')):
            brief.facts = request.json['brief']['facts']
        # --- issues
        if (request.json.get('brief').get('issues')):
            brief.issues = request.json['brief']['issues']
        # --- updated at
        brief.updated_at = datetime.now()
        # --- commit 
        session.add(brief)
    return json({ 'status': 'success' })


# CAP / CASELAW
@api_app.route('/v1/cap/case/index', methods = ['POST'])
@auth_route
async def app_route_cap_case_index(request):
    session = request.ctx.session
    cap_ids = request.json.get('cap_ids') or []
    project_tag = request.json.get('project_tag')
    # --- fetch/insert via CAP api
    async with session.begin():
        for cap_id in cap_ids:
            await upsert_cap_case(session, cap_id, project_tag)
    # --- queue jobs after initial fetch/insert
    arq_pool = await create_queue_pool()
    for cap_id in cap_ids:
        await arq_pool.enqueue_job('job_index_cap_case', cap_id)
    return json({ 'status': 'success' })

@api_app.route('/v1/cap/case/<cap_id>', methods = ['GET'])
@auth_route
async def app_route_cap_case_get(request, cap_id):
    session = request.ctx.session
    async with session.begin():
        query_cap_caselaw = await session.execute(
            sa.select(CAPCaseLaw).where(CAPCaseLaw.cap_id == int(cap_id)))
        cap_case = query_cap_caselaw.scalar_one_or_none()
    return json({ 'status': 'success', 'data': { 'cap_case': cap_case.serialize() } })

@api_app.route('/v1/cap/case/<cap_id>', methods = ['DELETE'])
@auth_route
async def app_route_cap_case_delete(request, cap_id):
    session = request.ctx.session
    async with session.begin():
        # --- cap case content & embeddings
        await deindex_cap_case(session, int(cap_id))
        # --- cap_case
        await session.execute(sa.delete(CAPCaseLaw)
            .where(CAPCaseLaw.cap_id == int(cap_id)))
    return json({ 'status': 'success' })

@api_app.route('/v1/cap/case/<cap_id>/extractions', methods = ['POST'])
@auth_route
async def app_route_cap_case_extractions(request, cap_id):
    session = request.ctx.session
    async with session.begin():
        await _index_cap_case_process_extractions(session=session, cap_id=int(cap_id))
    return json({ 'status': 'success' })

@api_app.route('/v1/cap/case/search', methods = ['GET'])
@auth_route
async def app_route_cap_case_search(request):
    session = request.ctx.session
    async with session.begin():
        query = request.args.get('query')
        cap_cases = await cap_api_search(session, query)
        cap_cases = serialize_list(cap_cases)
    return json({ 'status': 'success', 'data': { 'cap_cases': cap_cases } })


# DOCUMENTS
@api_app.route('/v1/document/<document_id>', methods = ['GET'])
@auth_route
async def app_route_document_get(request, document_id):
    session = request.ctx.session
    async with session.begin():
        query_document = await session.execute(
            sa.select(Document)
                .options(
                    selectinload(Document.content)
                        .options(selectinload(DocumentContent.image_file)),
                    selectinload(Document.files))
                .where(Document.id == int(document_id))
        )
        document = query_document.scalars().first()
        # TODO: figure out how to more elegantly pull off serialized properties
        def map_content(cn):
            payload = cn.serialize()
            if (cn.image_file != None):
                payload['image_file'] = cn.image_file.serialize()
            return payload
        document_json = document.serialize()
        document_json['content'] = list(map(map_content, document.content))
        document_json['files'] = serialize_list(document.files)
    return json({ 'status': 'success', 'data': { 'document': document_json } })

@api_app.route('/v1/document/<document_id>', methods = ['DELETE'])
@auth_route
async def app_route_document_delete(request, document_id):
    session = request.ctx.session
    async with session.begin():
        # --- document content & embeddings
        await deindex_document(session, document_id)
        # --- files
        await session.execute(sa.update(File)
            .where(File.document_id == int(document_id))
            .values(document_id=None))
        # --- document
        await session.execute(sa.delete(Document)
            .where(Document.id == int(document_id)))
    return json({ 'status': 'success' })

@api_app.route('/v1/document/<document_id>/extractions', methods = ['POST'])
@auth_route
async def app_route_document_extractions(request, document_id):
    # queue up
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_process_document_extras', document_id)
    # respond
    return json({ 'status': 'success' })

@api_app.route('/v1/documents', methods = ['GET'])
@auth_route
async def app_route_documents(request):
    session = request.ctx.session
    async with session.begin():
        # --- query
        query_builder_documents = sa.select(Document).options(subqueryload(Document.content), subqueryload(Document.files))
        # --- filter based on params / TODO: is there a better way to do this?
        if request.args.get('case_id'):
            query_builder_documents = query_builder_documents.where(Document.case_id == int(request.args.get('case_id')))
        if request.args.get('organization_id'):
            query_builder_documents = query_builder_documents.where(Document.organization_id == int(request.args.get('organization_id')))
        if request.args.get('user_id'):
            query_builder_documents = query_builder_documents.where(Document.user_id == int(request.args.get('user_id')))
        # --- exec fetch w/ ordering
        query_documents = await session.execute(query_builder_documents.order_by(sa.desc(Document.id)))
        documents = query_documents.scalars().unique().all()
        # there's got to be a better way to deal w/ this
        def map_documents_and_content(d):
            doc = d.serialize()
            doc['content'] = list(filter(
                lambda c: c['tokenizing_strategy'] == 'sentence',
                serialize_list(d.content)))
            doc['files'] = serialize_list(d.files)
            return doc
        documents_json = list(map(map_documents_and_content, documents))
    return json({ 'status': 'success', "documents": documents_json })


# INDEXERS
@api_app.route('/v1/index/document/pdf', methods = ['POST'])
@auth_route
async def app_route_index_document_pdf(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id')) if request.args.get('case_id') else None
    organization_id = int(request.args.get('organization_id')) if request.args.get('organization_id') else None
    user_id = int(request.args.get('user_id')) if request.args.get('user_id') else None
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, type="pdf", case_id=case_id, organization_id=organization_id, user_id=user_id)
    await session.commit()
    # --- queue processing
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_index_document_pdf', document_id)
    return json({ 'status': 'success', 'data': { 'document': { 'id': document_id } } })

@api_app.route('/v1/index/document/docx', methods = ['POST'])
@auth_route
async def app_route_index_document_docx(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id')) if request.args.get('case_id') else None
    organization_id = int(request.args.get('organization_id')) if request.args.get('organization_id') else None
    user_id = int(request.args.get('user_id')) if request.args.get('user_id') else None
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, type="docx", case_id=case_id, organization_id=organization_id, user_id=user_id)
    await session.commit()
    # --- queue processing
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_index_document_docx', document_id)
    return json({ 'status': 'success', 'data': { 'document': { 'id': document_id } } })

@api_app.route('/v1/index/document/image', methods = ['POST'])
@auth_route
async def app_route_index_document_image(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id')) if request.args.get('case_id') else None
    organization_id = int(request.args.get('organization_id')) if request.args.get('organization_id') else None
    user_id = int(request.args.get('user_id')) if request.args.get('user_id') else None
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, type="image", case_id=case_id, organization_id=organization_id, user_id=user_id)
    await session.commit()
    # --- queue processing
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_index_document_image', document_id)
    return json({ 'status': 'success', 'data': { 'document': { 'id': document_id } } })

@api_app.route('/v1/index/document/audio', methods = ['POST'])
@auth_route
async def app_route_index_document_audio(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id')) if request.args.get('case_id') else None
    organization_id = int(request.args.get('organization_id')) if request.args.get('organization_id') else None
    user_id = int(request.args.get('user_id')) if request.args.get('user_id') else None
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, type="audio", case_id=case_id, organization_id=organization_id, user_id=user_id)
    await session.commit()
    # --- queue processing
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_index_document_audio', document_id)
    return json({ 'status': 'success', 'data': { 'document': { 'id': document_id } } })

@api_app.route('/v1/index/document/video', methods = ['POST'])
@auth_route
async def app_route_index_document_video(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id')) if request.args.get('case_id') else None
    organization_id = int(request.args.get('organization_id')) if request.args.get('organization_id') else None
    user_id = int(request.args.get('user_id')) if request.args.get('user_id') else None
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, type="video", case_id=case_id, organization_id=organization_id, user_id=user_id)
    await session.commit()
    # --- queue processing
    arq_pool = await create_queue_pool()
    await arq_pool.enqueue_job('job_index_document_video', document_id)
    return json({ 'status': 'success', 'data': { 'document': { 'id': document_id } } })


# HEALTH
@api_app.route('/health', methods = ['GET'])
def app_route_health(request):
    return json({ 'status': 'success' })


# HIGHLIGHTS (TODO: removed this concept, will re-introduce when desired)
@api_app.route('/v1/highlights', methods = ['GET'])
@auth_route
async def app_route_highlights(request):
    highlights = []
    return json({ 'status': 'success', "highlights": highlights })


# ORGANIZATIONS
@api_app.route('/v1/organizations', methods = ['GET'])
@auth_route
async def app_route_organizations(request):
    session = request.ctx.session
    async with session.begin():
        query_orgs = await session.execute(
            sa.select(Organization)
                .options(
                    joinedload(Organization.users),
                    joinedload(Organization.writings)
                ))
        organizations_models = query_orgs.scalars().unique().all()
        # organizations_json = serialize_list(organizations_models)
        # TODO: FFS how do we serialize simply... keep getting async io errors
        # https://github.com/n0nSmoker/SQLAlchemy-serializer
        # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
        # organizations_json = list(map(lambda o: o.to_dict(), organizations_models))
        organizations_json = list(map(lambda o: o.serialize(['users', 'writings']), organizations_models))
    return json({ 'status': 'success', 'data': { 'organizations': organizations_json } })

@api_app.route('/v1/organization', methods = ['POST'])
@auth_route
async def app_route_organization_post(request):
    session = request.ctx.session
    async with session.begin():
        # --- insert organization w/ user (model mapping/definition knows how to insert w/ junction table)
        organization_to_insert = Organization(
            ai_action_locks=generate_ai_action_locks(),
            created_at=datetime.now(),
            name=request.json['name'],
        )
        session.add(organization_to_insert)
    return json({ 'status': 'success', 'data': { "organization": { "id": organization_to_insert.id } } })

@api_app.route('/v1/organization/<organization_id>/ai_action_locks_reset', methods = ['PUT'])
@auth_route
async def app_route_organization_put_action_locks(request, organization_id):
    session = request.ctx.session
    async with session.begin():
        organization_id = int(organization_id)
        # --- delete existing action locks
        await session.execute(sa.delete(AIActionLock).where(AIActionLock.organization_id == organization_id))
        # --- add new action locks
        session.add_all(generate_ai_action_locks(organization_id=organization_id))
    return json({ 'status': 'success' })

@api_app.route('/v1/organization/<organization_id>/user', methods = ['POST'])
@auth_route
async def app_route_organization_user(request, organization_id):
    session = request.ctx.session
    action = request.json.get('action')
    query_org = await session.execute(
        sa.select(Organization)
            .options(joinedload(Organization.users))
            .where(Organization.id == int(organization_id)))
    organization = query_org.scalars().unique().one()
    # --- if adding
    if action == 'add':
        # --- check if user exists or not via email (TODO: user_id)
        user_email = request.json.get('user').get('email')
        query_user = await session.execute(sa.select(User).where(User.email == user_email))
        user = query_user.scalar_one_or_none()
        if user != None:
            organization.users.append(user)
            session.add(organization)
        else:
            user_to_insert = User(
                name=request.json.get('user').get('name'),
                email=request.json.get('user').get('email'),
                ai_action_locks=generate_ai_action_locks(),
                organizations=[organization]
            )
            session.add(user_to_insert)
    # --- if removing
    elif action == 'remove':
        user_id = request.json.get('user_id')
        query_user = await session.execute(sa.select(User).where(User.id == int(user_id)))
        user = query_user.scalars().one()
        for u in organization.users:
            if u.id == user.id:
                organization.users.remove(u)
                session.add(organization)
    # --- save
    await session.commit()
    return json({ 'status': 'success' })


# WRITING
@api_app.route('/v1/writings', methods = ['GET'])
@auth_route
async def app_route_writings_get(request):
    session = request.ctx.session
    async with session.begin():
        query_builder = sa.select(Writing).order_by(sa.desc(Writing.id))
        # --- filter for org or case related writing
        if (request.args.get('case_id')):
            query_builder = query_builder.where(Writing.case_id == int(request.args.get('case_id')))
        elif (request.args.get('organization_id')):
            query_builder = query_builder.where(Writing.organization_id == int(request.args.get('organization_id')))
        # --- filter for templates
        if (request.args.get('is_template')):
            is_template_true = request.args.get('is_template') == 'true'
            if (is_template_true):
                query_builder= query_builder.where(Writing.is_template == True)
            else:
                query_builder= query_builder.where(sa.or_(Writing.is_template == False, Writing.is_template == None))
        query_writings = await session.execute(query_builder)
        writings = query_writings.scalars().all()
        writings_json = serialize_list(writings)
    return json({ 'status': 'success', 'data': { 'writings': writings_json } })

@api_app.route('/v1/writing/<writing_id>', methods = ['GET'])
@auth_route
async def app_route_writing_get(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        query_writing = await session.execute(
            sa.select(Writing).where(Writing.id == int(writing_id)))
        writing = query_writing.scalar_one_or_none()
        writing_json = writing.serialize()
    return json({ 'status': 'success', "writing": writing_json })

@api_app.route('/v1/writing/<writing_id>/docx', methods = ['GET'])
@auth_route
async def app_route_writing_get_docx(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        # get writing w/ html
        query_writing = await session.execute(
            sa.select(Writing).where(Writing.id == int(writing_id)))
        writing = query_writing.scalar_one_or_none()
        # create docx
        h2d_parser = HtmlToDocx()
        writing_docx = h2d_parser.parse_html_string(writing.body_html)
        # save to disk
        writing_docx_path = f'/tmp/writing_docx_{writing_id}.docx'
        writing_docx.save(writing_docx_path)
        # TODO: clean up file
        # respond
        return await response.file(writing_docx_path)

@api_app.route('/v1/writing', methods = ['POST'])
@auth_route
async def app_route_writings_post(request):
    session = request.ctx.session
    writing_model = Writing(
        body_html=request.json.get('writing').get('body_html'),
        body_text=request.json.get('writing').get('body_text'),
        case_id=request.json.get('writing').get('case_id'),
        is_template=request.json.get('writing').get('is_template'),
        name=request.json.get('writing').get('name'),
        organization_id=request.json.get('writing').get('organization_id'),
        forked_writing_id=int(request.json.get('writing').get('forked_writing_id')) if request.json.get('writing').get('forked_writing_id') != None else None,
    )
    session.add(writing_model)
    await session.commit()
    return json({ 'status': 'success' })

@api_app.route('/v1/writing/<writing_id>', methods = ['PUT'])
@auth_route
async def app_route_writing_put(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        query_writing = await session.execute(
            sa.select(Writing).where(Writing.id == int(writing_id)))
        writing = query_writing.scalars().one()
        # TODO: make better lol
        if (request.json.get('writing').get('name')):
            writing.name = request.json['writing']['name']
        if (request.json.get('writing').get('body_html')):
            writing.body_html = request.json['writing']['body_html']
        if (request.json.get('writing').get('body_text')):
            writing.body_text = request.json['writing']['body_text']
        writing.updated_at = datetime.now()
        session.add(writing)
    return json({ 'status': 'success' })

@api_app.route('/v1/writing/<writing_id>', methods = ['DELETE'])
@auth_route
async def app_route_writing_delete(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        # --- delete embeddings & vector db
        await deindex_writing(session, writing_id)
        # --- delete writing
        await session.execute(sa.delete(Writing)
            .where(Writing.id == int(writing_id)))
    return json({ 'status': 'success' })


# USERS
@api_app.route('/v1/users', methods = ['GET'])
@auth_route
async def app_route_users(request):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User))
        users = query_user.scalars()
        user_json = serialize_list(users)
    return json({ 'status': 'success', "users": user_json })

@api_app.route('/v1/user/<user_id>', methods = ['GET'])
@auth_route
async def app_route_user(request, user_id):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User).where(User.id == int(user_id)))
        user = query_user.scalar_one_or_none()
        # TODO: figure out how to do these serialize() calls recurisvely within user.serialize()
        user_json = user.serialize() 
    return json({ 'status': 'success', "user": user_json })

@api_app.route('/v1/user/<user_id>', methods = ['PUT'])
@auth_route
async def app_route_user_put(request, user_id):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(
            sa.select(User).where(User.id == int(user_id)))
        user = query_user.scalars().one()
        # TODO: make better lol
        if (request.json.get('user').get('name')):
            user.name = request.json['user']['name']
        if (request.json.get('user').get('password')):
            user.password = request.json['user']['password']
        session.add(user)
    return json({ 'status': 'success' })

@api_app.route('/v1/user/<user_id>/ai_action_locks_reset', methods = ['PUT'])
@auth_route
async def app_route_user_put_action_locks(request, user_id):
    session = request.ctx.session
    async with session.begin():
        user_id = int(user_id)
        # --- delete existing action locks
        await session.execute(sa.delete(AIActionLock).where(AIActionLock.user_id == user_id))
        # --- add new action locks
        session.add_all(generate_ai_action_locks(user_id=user_id))
    return json({ 'status': 'success' })


# RUN
def start_api():
    host = env.env_get_gideon_api_host()
    port = env.env_get_gideon_api_port()
    # RUN API WORKERS
    api_app.run(
        host=host,
        port=port,
        auto_reload=False, # auto-reload only for dev. done via watchdog pkg in docker-compose file
        workers=2) # whether 1 or 2 workers, sits at 3.8GB memory usage
 