from contextvars import ContextVar
from datetime import datetime
import logging
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from strawberry.sanic.views import GraphQLView
import sqlalchemy as sa
from sqlalchemy.orm import joinedload, selectinload, subqueryload

from agents.generate_ai_action_locks import generate_ai_action_locks
from auth.auth_route import auth_route
from auth.token import decode_token, encode_token
from dbs.sa_models import serialize_list, AIActionLock, Case, CaseFact, Document, DocumentContent, File, Organization, Writing, User
from dbs.sa_sessions import create_sqlalchemy_session
import env
from indexers.deindex_document import deindex_document
from indexers.index_document_audio import _index_document_audio_process_extractions
from indexers.index_document_image import _index_document_image_process_extractions
from indexers.index_document_pdf import _index_document_pdf_process_extractions
from indexers.index_document_video import _index_document_video_process_extractions
from indexers.processors.job_index_cap_caselaw import job_index_cap_caselaw
from indexers.processors.job_index_document_audio import job_index_document_audio
from indexers.processors.job_index_document_image import job_index_document_image
from indexers.processors.job_index_document_pdf import job_index_document_pdf
from indexers.processors.job_index_document_video import job_index_document_video
from indexers.utils.index_document_prep import index_document_prep
from queries.question_answer import question_answer
from queries.search_locations import search_locations
from queries.utils.serialize_location import serialize_location
from queries.write_template_with_ai import write_template_with_ai
from queues import indexing_queue

# INIT
app = Sanic('api')
app.config['RESPONSE_TIMEOUT'] = 60 * 30 # HACK: until we move pdf processing outside the api endpoints, disallowing 503 timeout responses now


# MIDDLEWARE
# --- cors
CORS(app)
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
_base_model_session_ctx = ContextVar('session')
@app.middleware('request')
async def inject_session(request):
    request.ctx.session = create_sqlalchemy_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@app.middleware('response')
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()

    
# AUTH
@app.route('/v1/auth/login', methods = ['POST'])
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

@app.route('/v1/auth/user', methods = ['GET'])
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
@app.route('/v1/ai/query-document-answer', methods = ['POST'])
@auth_route
async def app_route_ai_query_document_answer(request):
    session = request.ctx.session
    async with session.begin():
        answer, locations = await question_answer(
            session,
            query_text=request.json.get('question'),
            case_id=request.json.get('case_id'))
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'answer': answer, 'locations': locations } })

@app.route('/v1/ai/query-document-locations', methods = ['POST'])
@auth_route
async def app_route_ai_query_document_locations(request):
    session = request.ctx.session
    async with session.begin():
        # Fetch
        locations = await search_locations(
            session,
            query_text=request.json.get('query'),
            case_id=request.json.get('case_id'))
        # Serialize (TODO): make 'Location' class rather than plain dict
        locations = list(map(serialize_location, locations))
    return json({ 'status': 'success', 'data': { 'locations': locations } })

@app.route('/v1/ai/fill-writing-template', methods = ['POST'])
@auth_route
async def app_route_ai_fill_writing_template(request):
    session = request.ctx.session
    # setup writing model
    writing_model = Writing(
        case_id=request.json.get('case_id'),
        is_template=request.json.get('is_template'),
        name=request.json.get('name'),
        organization_id=request.json.get('organization_id'),
        forked_writing_id=int(request.json.get('forked_writing_id')) if request.json.get('forked_writing_id') != None else None,
    )
    # pass it to ai writer
    updated_writing_model = await write_template_with_ai(session, writing_model)
    # save
    session.add(updated_writing_model)
    await session.commit()
    return json({ 'status': 'success' })


# CASES
@app.route('/v1/cases', methods = ['GET'])
@auth_route
async def app_route_cases(request):
    session = request.ctx.session
    async with session.begin():
        cases_json = []
        query_user = await session.execute(
            sa.select(User)
                .options(selectinload(User.cases))
                .where(User.id == int(request.args.get('user_id')))
        )
        user = query_user.scalar_one_or_none()
        cases_json = serialize_list(user.cases)
    return json({ 'status': 'success', "cases": cases_json })

@app.route('/v1/case/<case_id>', methods = ['GET'])
@auth_route
async def app_route_case_get(request, case_id):
    session = request.ctx.session
    async with session.begin():
        query_case = await session.execute(
            sa.select(Case).where(Case.id == int(case_id)))
        case = query_case.scalar_one_or_none()
        case_json = case.serialize()
    return json({ 'status': 'success', "case": case_json })

@app.route('/v1/case/<case_id>', methods = ['PUT'])
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

@app.route('/v1/case/<case_id>/ai_action_locks_reset', methods = ['PUT'])
@auth_route
async def app_route_case_put_action_locks(request, case_id):
    session = request.ctx.session
    async with session.begin():
        case_id = int(case_id)
        # --- delete existing action locks
        await session.execute(sa.delete(AIActionLock)
            .where(AIActionLock.case_id == case_id))
        # --- add new action locks
        session.add_all(generate_ai_action_locks(case_id))
    return json({ 'status': 'success' })

@app.route('/v1/case/<case_id>/reindex_all_documents', methods = ['PUT'])
@auth_route
async def app_route_case_put_reprocess_all_data(request, case_id):
    session = request.ctx.session
    async with session.begin():
        case_id = int(case_id)
        query_documents = await session.execute(sa.select(Document).where(Document.case_id == case_id))
        documents = query_documents.scalars().all()
        # --- for each document, delete embeddings, document content, remove from vector dbs/indexes
        for document in documents:
            await deindex_document(session, document.id)
    # --- for each document, re-run document processing + embedding + vector db/index upsertion
    for document in documents:
        if document.type == 'pdf':
            indexing_queue.enqueue(job_index_document_pdf, document.id)
        if document.type == 'image':
            indexing_queue.enqueue(job_index_document_image, document.id)
        if document.type == 'audio':
            indexing_queue.enqueue(job_index_document_audio, document.id)
        if document.type == 'video':
            indexing_queue.enqueue(job_index_document_video, document.id)
    return json({ 'status': 'success' })

@app.route('/v1/case', methods = ['POST'])
@auth_route
async def app_route_case_post(request):
    session = request.ctx.session
    async with session.begin():
        # --- get user for relation
        query_user = await session.execute(sa.select(User).where(User.id == int(request.json['userId'])))
        user = query_user.scalars().one()
        # --- insert case w/ user (model mapping/definition knows how to insert w/ junction table)
        case_to_insert = Case(
            ai_action_locks=generate_ai_action_locks(),
            users=[user]
        )
        session.add(case_to_insert)
    return json({ 'status': 'success', "case": { "id": case_to_insert.id } })


# CASE FACTS
@app.route('/v1/case_facts', methods = ['GET'])
@auth_route
async def app_route_case_facts_get(request):
    session = request.ctx.session
    async with session.begin():
        query_builder = sa.select(CaseFact).order_by(sa.desc(CaseFact.id))
        # --- filter for org or case related case_fact
        if (request.args.get('case_id')):
            query_builder = query_builder.where(CaseFact.case_id == int(request.args.get('case_id')))
        query_case_facts = await session.execute(query_builder)
        case_facts = query_case_facts.scalars().all()
        case_facts_json = serialize_list(case_facts)
    return json({ 'status': 'success', 'data': { 'case_facts': case_facts_json } })

@app.route('/v1/case_fact/<case_fact_id>', methods = ['GET'])
@auth_route
async def app_route_case_fact_get(request, case_fact_id):
    session = request.ctx.session
    async with session.begin():
        query_case_fact = await session.execute(
            sa.select(CaseFact).where(CaseFact.id == int(case_fact_id)))
        case_fact = query_case_fact.scalar_one_or_none()
        case_fact_json = case_fact.serialize()
    return json({ 'status': 'success', "case_fact": case_fact_json })

@app.route('/v1/case_fact', methods = ['POST'])
@auth_route
async def app_route_case_facts_post(request):
    session = request.ctx.session
    case_fact_model = CaseFact(
        case_id=request.json.get('case_id'),
    )
    session.add(case_fact_model)
    await session.commit()
    return json({ 'status': 'success', })

@app.route('/v1/case_fact/<case_fact_id>', methods = ['PUT'])
@auth_route
async def app_route_case_fact_put(request, case_fact_id):
    session = request.ctx.session
    async with session.begin():
        query_case_fact = await session.execute(
            sa.select(CaseFact).where(CaseFact.id == int(case_fact_id)))
        case_fact = query_case_fact.scalars().one()
        # TODO: make better lol
        if (request.json.get('case_fact').get('text')):
            case_fact.text = request.json['case_fact']['text']
        session.add(case_fact)
    return json({ 'status': 'success' })

@app.route('/v1/case_fact/<case_fact_id>', methods = ['DELETE'])
@auth_route
async def app_route_case_fact_delete(request, case_fact_id):
    session = request.ctx.session
    async with session.begin():
        # --- case_fact
        await session.execute(sa.delete(CaseFact)
            .where(CaseFact.id == int(case_fact_id)))
    return json({ 'status': 'success' })


# CASELAW
@app.route('/v1/cap/caselaw/index', methods = ['POST'])
@auth_route
async def app_route_cap_caselaw_index(request):
    session = request.ctx.session
    async with session.begin():
        cap_ids = request.json['cap_ids']
        for cap_id in cap_ids:
            indexing_queue.enqueue(job_index_cap_caselaw, cap_id)
    return json({ 'status': 'success' })


# DOCUMENTS
@app.route('/v1/document/<document_id>', methods = ['GET'])
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

@app.route('/v1/document/<document_id>', methods = ['DELETE'])
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

@app.route('/v1/document/<document_id>/extractions', methods = ['POST'])
@auth_route
async def app_route_document_extractions(request, document_id):
    session = request.ctx.session
    async with session.begin():
        query_document = await session.execute(
            sa.select(Document).where(Document.id == int(document_id)))
        document = query_document.scalars().first()
        if (document.type == "pdf"):
            await _index_document_pdf_process_extractions(session=session, document_id=document.id)
        if (document.type == "image"):
            await _index_document_image_process_extractions(session=session, document_id=document.id)
        if (document.type == "audio"):
            await _index_document_audio_process_extractions(session=session, document_id=document.id)
        if (document.type == "video"):
            await _index_document_video_process_extractions(session=session, document_id=document.id)
    return json({ 'status': 'success' })

@app.route('/v1/documents', methods = ['GET'])
@auth_route
async def app_route_documents(request):
    session = request.ctx.session
    async with session.begin():
        query_documents = await session.execute(
            sa.select(Document)
                .options(subqueryload(Document.content), subqueryload(Document.files))
                .where(Document.case_id == int(request.args.get('case_id')))
                .order_by(sa.desc(Document.id)))
        documents = query_documents.scalars().all()
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
@app.route('/v1/index/document/pdf', methods = ['POST'])
@auth_route
async def app_route_index_document_pdf(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id'))
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, case_id=case_id, type="pdf")
    await session.commit()
    # --- queue processing
    indexing_queue.enqueue(job_index_document_pdf, document_id)
    return json({ 'status': 'success' })

@app.route('/v1/index/document/image', methods = ['POST'])
@auth_route
async def app_route_index_document_image(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id'))
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, case_id=case_id, type="image")
    await session.commit()
    # --- queue processing
    indexing_queue.enqueue(job_index_document_image, document_id)
    return json({ 'status': 'success' })

@app.route('/v1/index/document/audio', methods = ['POST'])
@auth_route
async def app_route_index_document_audio(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id'))
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, case_id=case_id, type="audio")
    await session.commit()
    # --- queue processing
    indexing_queue.enqueue(job_index_document_audio, document_id)
    return json({ 'status': 'success' })

@app.route('/v1/index/document/video', methods = ['POST'])
@auth_route
async def app_route_index_document_video(request):
    pyfile = request.files['file'][0]
    session = request.ctx.session
    case_id = int(request.args.get('case_id'))
    # --- setup document + file
    document_id = await index_document_prep(session, pyfile=pyfile, case_id=case_id, type="video")
    await session.commit()
    # --- queue processing
    indexing_queue.enqueue(job_index_document_video, document_id)
    return json({ 'status': 'success' })


# HEALTH
@app.route('/health', methods = ['GET'])
def app_route_health(request):
    return json({ 'status': 'success' })


# HIGHLIGHTS (TODO: removed this concept, will re-introduce when desired)
@app.route('/v1/highlights', methods = ['GET'])
@auth_route
async def app_route_highlights(request):
    highlights = []
    return json({ 'status': 'success', "highlights": highlights })


# ORGANIZATIONS
@app.route('/v1/organizations', methods = ['GET'])
@auth_route
async def app_route_organizations(request):
    session = request.ctx.session
    async with session.begin():
        query_orgs = await session.execute(
            sa.select(Organization)
                .options(
                    joinedload(Organization.users),
                    joinedload(Organization.writing_templates)
                ))
        organizations_models = query_orgs.scalars().unique().all()
        # organizations_json = serialize_list(organizations_models)
        # TODO: FFS how do we serialize simply... keep getting async io errors
        # https://github.com/n0nSmoker/SQLAlchemy-serializer
        # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
        # organizations_json = list(map(lambda o: o.to_dict(), organizations_models))
        organizations_json = list(map(lambda o: o.serialize(['users', 'writing_templates']), organizations_models))
    return json({ 'status': 'success', 'data': { 'organizations': organizations_json } })


# WRITING
@app.route('/v1/writings', methods = ['GET'])
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

@app.route('/v1/writing/<writing_id>', methods = ['GET'])
@auth_route
async def app_route_writing_get(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        query_writing = await session.execute(
            sa.select(Writing).where(Writing.id == int(writing_id)))
        writing = query_writing.scalar_one_or_none()
        writing_json = writing.serialize()
    return json({ 'status': 'success', "writing": writing_json })

@app.route('/v1/writing', methods = ['POST'])
@auth_route
async def app_route_writings_post(request):
    session = request.ctx.session
    writing_model = Writing(
        body_html=request.json.get('body_html'),
        body_text=request.json.get('body_text'),
        case_id=request.json.get('case_id'),
        is_template=request.json.get('is_template'),
        name=request.json.get('name'),
        organization_id=request.json.get('organization_id'),
        forked_writing_id=int(request.json.get('forked_writing_id')) if request.json.get('forked_writing_id') != None else None,
    )
    session.add(writing_model)
    await session.commit()
    return json({ 'status': 'success' })

@app.route('/v1/writing/<writing_id>', methods = ['PUT'])
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
        session.add(writing)
    return json({ 'status': 'success' })

@app.route('/v1/writing/<writing_id>', methods = ['DELETE'])
@auth_route
async def app_route_writing_delete(request, writing_id):
    session = request.ctx.session
    async with session.begin():
        # --- writing
        await session.execute(sa.delete(Writing)
            .where(Writing.id == int(writing_id)))
    return json({ 'status': 'success' })


# USERS
@app.route('/v1/user/<user_id>', methods = ['GET'])
@auth_route
async def app_route_user(request, user_id):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User).where(User.id == int(user_id)))
        user = query_user.scalar_one_or_none()
        # TODO: figure out how to do these serialize() calls recurisvely within user.serialize()
        user_json = user.serialize() 
    return json({ 'status': 'success', "user": user_json })

@app.route('/v1/users', methods = ['GET'])
@auth_route
async def app_route_users(request):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User))
        users = query_user.scalars()
        user_json = serialize_list(users)
    return json({ 'status': 'success', "users": user_json })


# RUN
def start_api():
    host = env.env_get_gideon_api_host()
    port = env.env_get_gideon_api_port()
    # RUN API WORKERS
    app.run(
        host=host,
        port=port,
        auto_reload=False, # auto-reload only for dev. done via watchdog pkg in docker-compose file
        workers=2) # whether 1 or 2 workers, sits at 3.8GB memory usage
 