from contextvars import ContextVar
from datetime import datetime
import pinecone
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, selectinload, subqueryload, sessionmaker

from auth.auth_route import auth_route
from auth.token import decode_token, encode_token
import env
from indexers.index_audio import index_audio, _index_audio_process_extractions
from indexers.index_image import index_image, _index_image_process_extractions
from indexers.index_pdf import index_pdf, _index_pdf_process_extractions
from indexers.index_vectors import index_vectors
from indexers.index_video import index_video, _index_video_process_extractions
from dbs.sa_models import serialize_list, Case, Document, DocumentContent, Embedding, File, User
from queries.question_answer import question_answer
from queries.search_for_locations_across_text import search_for_locations_across_text
from queries.search_for_locations_across_image import search_for_locations_across_image
from dbs.vectordb_pinecone import get_indexes


# INIT
app = Sanic('api')
app.config['RESPONSE_TIMEOUT'] = 60 * 30 # HACK: until we move pdf processing outside the api endpoints, disallowing 503 timeout responses now


# MIDDLEWARE
# --- cors
CORS(app)
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
sqlalchemy_bind = create_async_engine(
    env.env_get_database_app_url(),
    echo=True,
    echo_pool='debug',
    max_overflow=20,
    pool_size=20,
    pool_reset_on_return=None,
)
_sessionmaker = sessionmaker(
    sqlalchemy_bind,
    AsyncSession,
    expire_on_commit=False,
    future=True,
)
_base_model_session_ctx = ContextVar('session')
@app.middleware('request')
async def inject_session(request):
    request.ctx.session = _sessionmaker()
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
        if (request.json['password'] != None and request.json['password'] == user.password):
            token = encode_token({ 'issued_at': datetime.now().timestamp(), 'user_id': user.id })
            return json({ 'status': 'success',  'token': token, 'user': user.serialize() })
        else:
            return json({ 'status': 'error' })

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


# CASES
@app.route('/v1/cases', methods = ['GET'])
@auth_route
async def app_route_cases(request):
    session = request.ctx.session
    async with session.begin():
        cases_json = []
        first_param_key, first_param_value = request.query_string.split('=') 
        if first_param_key == "user_id":
            query_user = await session.execute(
                sa.select(User)
                    .options(selectinload(User.cases))
                    .where(User.id == int(first_param_value))
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
        # TODO: make this better lol
        case.name = request.json['case']['name']
        session.add(case)
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
        case_to_insert = Case(users=[user])
        session.add(case_to_insert)
        await session.flush()
    return json({ 'status': 'success', "case": { "id": case_to_insert.id } })


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
        document_json = document.serialize()
        document_json['content'] = serialize_list(document.content)
        document_json['files'] = serialize_list(document.files)
    return json({ 'status': 'success', "document": document_json })

@app.route('/v1/document/<document_id>', methods = ['DELETE'])
@auth_route
async def app_route_document_delete(request, document_id):
    session = request.ctx.session
    async with session.begin():
        # FETCH
        # --- embeddings
        query_embeddings = await session.execute(
            sa.select(Embedding).options(
                joinedload(Embedding.document_content).options(
                    joinedload(DocumentContent.document)
            )).where(Embedding.document_content.has(
                DocumentContent.document.has(
                    Document.id == int(document_id)))))
        embeddings = query_embeddings.scalars().all()
        embeddings_ids_ints = list(map(lambda e: e.id, embeddings))
        embeddings_ids_strs = list(map(lambda id: str(id), embeddings_ids_ints))
        # DELETE INDEX VECTORS (via embedidngs)
        if (len(embeddings_ids_strs) > 0):
            get_indexes()["index_documents_clip"].delete(ids=embeddings_ids_strs)
            get_indexes()["index_documents_text"].delete(ids=embeddings_ids_strs)
            get_indexes()["index_documents_sentences"].delete(ids=embeddings_ids_strs)
        # DELETE MODELS
        # --- embeddings
        await session.execute(sa.delete(Embedding)
            .where(Embedding.id.in_(embeddings_ids_ints)))
        # --- document_content
        await session.execute(sa.delete(DocumentContent)
            .where(DocumentContent.document_id == int(document_id)))
        # --- files
        await session.execute(sa.update(File)
            .where(File.document_id == int(document_id))
            .values(document_id=None))
        # --- document
        await session.execute(sa.delete(Document)
            .where(Document.id == int(document_id)))
    return json({ 'status': 'success' })

@app.route('/v1/document/<document_id>/summarize', methods = ['POST'])
@auth_route
async def app_route_document_summarize(request, document_id):
    session = request.ctx.session
    async with session.begin():
        query_document = await session.execute(
            sa.select(Document).where(Document.id == int(document_id)))
        document = query_document.scalars().first()
        if (document.type == "pdf"):
            await _index_pdf_process_extractions(session=session, document_id=document.id)
        if (document.type == "image"):
            await _index_image_process_extractions(session=session, document_id=document.id)
        if (document.type == "audio"):
            await _index_audio_process_extractions(session=session, document_id=document.id)
        if (document.type == "video"):
            await _index_video_process_extractions(session=session, document_id=document.id)
    return json({ 'status': 'success' })

@app.route('/v1/documents', methods = ['GET'])
@auth_route
async def app_route_documents(request):
    session = request.ctx.session
    async with session.begin():
        query_documents = await session.execute(
            sa.select(Document)
                .options(subqueryload(Document.content), subqueryload(Document.files))
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

@app.route('/v1/documents/index/pdf', methods = ['POST'])
@auth_route
async def app_route_documents_index_pdf(request):
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/pdf/embeddings
        document_id = await index_pdf(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ 'status': 'success' })

@app.route('/v1/documents/index/image', methods = ['POST'])
@auth_route
async def app_route_documents_index_image(request):
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/embeddings
        document_id = await index_image(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ 'status': 'success' })

@app.route('/v1/documents/index/audio', methods = ['POST'])
@auth_route
async def app_route_documents_index_audio(request): 
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/embeddings
        document_id = await index_audio(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ 'status': 'success' })

@app.route('/v1/documents/index/video', methods = ['POST'])
@auth_route
async def app_route_documents_index_video(request): 
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/embeddings
        document_id = await index_video(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ 'status': 'success' })


# HIGHLIGHTS
@app.route('/v1/highlights', methods = ['GET'])
@auth_route
async def app_route_highlights(request):
    highlights = [] # get_highlights_json()
    return json({ 'status': 'success', "highlights": highlights })

# @app.route('/v1/highlights', methods = ['POST'])
# @auth_route
# def app_route_highlight_create(request):
#     highlight = request.json['highlight']
#     # --- process highlight embedding + save
#     highlight = index_highlight(
#         filename=highlight['filename'],
#         user=highlight['user'],
#         document_text_vectors_by_sentence_start_index=highlight['document_text_vectors_by_sentence_start_index'],
#         document_text_vectors_by_sentence_end_index=highlight['document_text_vectors_by_sentence_end_index'],
#         highlight_text=highlight['highlight_text'],
#         note_text=highlight['note_text']
#     )
#     # --- respond
#     return json({ 'status': 'success' })


# INDEXES
@app.route('/v1/index/<index_name>', methods = ['DELETE'])
@auth_route
def app_route_index_delete(request, index_name):
    index_to_clear = pinecone.Index(index_name)
    index_to_clear.delete(deleteAll=True) # just deletes all vectors
    return json({ 'status': 'success' })


# QUERIES   
@app.route('/v1/queries/document-query', methods = ['POST'])
@auth_route
async def app_route_question_answer(request):
    session = request.ctx.session
    async with session.begin():
        answer = await question_answer(session, request.json['question'])
    return json({ 'status': 'success', "answer": answer })

@app.route('/v1/queries/documents-locations', methods = ['POST'])
@auth_route
async def app_route_query_info_locations(request):
    session = request.ctx.session
    async with session.begin():
        def serialize_location(location):
            return dict(
                document=location['document'].serialize(),
                document_content=location['document_content'].serialize(),
                score=location['score']
            )
        # --- pdfs/transcripts
        locations_across_text = await search_for_locations_across_text(session, request.json['query'])
        locations_across_text_serialized = list(map(serialize_location, locations_across_text))
        # --- images
        locations_across_image = await search_for_locations_across_image(session, request.json['query'])
        locations_across_image_serialized = list(map(serialize_location, locations_across_image))
        # --- combined
        locations = locations_across_image_serialized + locations_across_text_serialized
    return json({ 'status': 'success', "locations": locations })

# @app.route('/v1/queries/highlights-query', methods = ['POST'])
# @auth_route
# def app_route_highlights_location(request):
#     # TODO: refactor
#     highlights = search_highlights(request.json['query'])
#     return json({ 'status': 'success', "highlights": highlights })

# @app.route('/v1/queries/summarize-user', methods = ['POST'])
# @auth_route
# def app_route_summarize_user(request):
#     user = request.json['user']
#     answer = summarize_user(user)
#     return json({ 'status': 'success', "answer": answer })

# @app.route('/v1/queries/contrast-users', methods = ['POST'])
# @auth_route
# def app_route_contrast_users(request):
#     user_one = request.json['user_one']
#     statement_one = summarize_user(user_one)
#     user_two = request.json['user_two']
#     statement_two = summarize_user(user_two)
#     answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
#     return json({ 'status': 'success', "answer": answer })


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
if __name__ == "__main__":
    # INIT WORKERS
    # TODO: recognize env var for auto_reload so we only have it in local
    # TODO: maybe use this forever serve for prod https://github.com/sanic-org/sanic/blob/main/examples/run_async.py
    # HACK: If I don't force single_process, OCR totally hangs
    app.run(
        host='0.0.0.0',
        port=3000,
        access_log=False,
        auto_reload=False,
        single_process=True,
    )
 