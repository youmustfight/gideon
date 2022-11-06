from contextvars import ContextVar
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker 

import env
from gideon_utils import get_file_path, get_documents_json, get_highlights_json, without_keys, write_file
from indexers.index_audio import index_audio
from indexers.index_highlight import index_highlight
from indexers.index_pdf import index_pdf, _index_pdf_process_embeddings, _index_pdf_process_extractions, _index_pdf_process_file
from indexers.index_image import index_image
from models import serialize_list, Case, Document, User
from queries.contrast_two_user_statements import contrast_two_user_statements
from queries.question_answer import question_answer
from queries.search_for_locations_across_text import search_for_locations_across_text
from queries.search_for_locations_across_image import search_for_locations_across_image
from queries.search_highlights import search_highlights
from queries.summarize_user import summarize_user


# INIT
app = Sanic("api")

# MIDDLEWARE
# --- cors
CORS(app)
# --- db driver + session context (https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.params.autocommit)
sqlalchemy_bind = create_async_engine(
    env.env_get_database_app_url(),
    echo=True,
    echo_pool="debug",
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
_base_model_session_ctx = ContextVar("session")
@app.middleware("request")
async def inject_session(request):
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


# AUTH
# TODO: actual auth
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
    return json({
        "success": True,
        "user": user.serialize(),
        # TODO: figure out how to do these serialize() calls recurisvely within user.serialize()
        # "cases": serialize_list(user.cases),
        # "organizations": serialize_list(user.organizations),
    })


# CASES
@app.route('/v1/cases', methods = ['GET'])
async def app_route_cases(request):
    session = request.ctx.session
    async with session.begin():
        cases_json = []
        first_param_key, first_param_value = request.query_string.split("=") 
        if first_param_key == "userId":
            query_user = await session.execute(
                sa.select(User)
                    .options(selectinload(User.cases))
                    .where(User.id == int(first_param_value))
            )
            user = query_user.scalar_one_or_none()
            cases_json = serialize_list(user.cases)
    return json({ "success": True, "cases": cases_json })

@app.route('/v1/case/<case_id>', methods = ['GET'])
async def app_route_case(request, case_id):
    session = request.ctx.session
    async with session.begin():
        query_case = await session.execute(
            sa.select(Case).where(Case.id == int(case_id))
        )
        case = query_case.scalar_one_or_none()
        case_json = case.serialize()
    return json({ "success": True, "case": case_json })


# DOCUMENTS
# TODO: safer file uploading w/ async: https://stackoverflow.com/questions/48930245/how-to-perform-file-upload-in-sanic
@app.route('/v1/documents/indexed', methods = ['GET'])
def app_route_documents(request):
    def reduced_json(j):
        return without_keys(j, [
            'document_text_vectors',
            'document_text_vectors_by_minute',
            'document_text_vectors_by_paragraph',
            # 'document_text_vectors_by_sentence',
        ])
        # Keep sentence vectors for frontend note tagging
    documents = get_documents_json()
    documents = list(map(reduced_json, documents)) # clear doc vectors
    return json({ "success": True, "documents": documents })

@app.route('/v1/documents/index/pdf', methods = ['POST'])
async def app_route_documents_index_pdf(request):
    session = request.ctx.session
    # with: ... is a python context creator
    # session.begin() returns a session obj that maintains begin/commit/rollback
    async with session.begin():
        pyfile = request.files['file'][0]
        await index_pdf(session=session, pyfile=pyfile)
        # await session.commit()
    # commits the transaction, closes the session
    return json({ "success": True })

@app.route('/v1/documents/index/pdf/<document_id>/process-file', methods = ['POST'])
async def app_route_documents_index_pdf_process_file(request, document_id):
    session = request.ctx.session
    async with session.begin():
        await _index_pdf_process_file(session=session, document_id=int(document_id))
    return json({ "success": True })

@app.route('/v1/documents/index/pdf/<document_id>/embeddings', methods = ['POST'])
async def app_route_documents_index_pdf_embeddings(request, document_id):
    session = request.ctx.session
    async with session.begin():
        await _index_pdf_process_embeddings(session=session, document_id=int(document_id))
    return json({ "success": True })

@app.route('/v1/documents/index/pdf/<document_id>/extractions', methods = ['POST'])
async def app_route_documents_index_pdf_extractions(request, document_id):
    session = request.ctx.session
    async with session.begin():
        await _index_pdf_process_extractions(session=session, document_id=int(document_id))
    return json({ "success": True })

@app.route('/v1/documents/index/audio', methods = ['POST'])
async def app_route_documents_index_audio(request): 
    session = request.ctx.session
    async with session.begin():
        file = request.files['file'][0]
        write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
        index_audio(session=session, filename=file.name)
    return json({ "success": True })

@app.route('/v1/documents/index/image', methods = ['POST'])
async def app_route_documents_index_image(request):
    session = request.ctx.session
    async with session.begin():
        file = request.files['file'][0]
        write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
        await index_image(session=session, filename=file.name)
    return json({ "success": True })


# HIGHLIGHTS

@app.route('/v1/highlights', methods = ['GET'])
def app_route_highlights(request):
    highlights = [] # get_highlights_json()
    return json({ "success": True, "highlights": highlights })

@app.route('/v1/highlights', methods = ['POST'])
def app_route_highlight_create(request):
    highlight = request.json['highlight']
    # --- process highlight embedding + save
    highlight = index_highlight(
        filename=highlight['filename'],
        user=highlight['user'],
        document_text_vectors_by_sentence_start_index=highlight['document_text_vectors_by_sentence_start_index'],
        document_text_vectors_by_sentence_end_index=highlight['document_text_vectors_by_sentence_end_index'],
        highlight_text=highlight['highlight_text'],
        note_text=highlight['note_text']
    )
    # --- respond
    return json({ "success": True })


# QUERIES
# TODO: class Document
# TODO: class DocumentQuery ({ text, image, vector })
# TODO: class DocumentQueryResult ({ ...what is currently a 'location' })

@app.route('/v1/queries/question-answer', methods = ['POST'])
def app_route_question_answer(request):
    answer = question_answer(request.json['question'], request.json['index_type'])
    return json({ "success": True, "answer": answer })

@app.route('/v1/queries/query-info-locations', methods = ['POST'])
def app_route_query_info_locations(request):
    locations_across_text = search_for_locations_across_text(request.json['query'])
    locations_across_image = search_for_locations_across_image(request.json['query'])
    # TODO: find a way to normalize scoring of GPT3 + CLIP
    locations = locations_across_text + locations_across_image
    return json({ "success": True, "locations": locations })

@app.route('/v1/queries/highlights-query', methods = ['POST'])
def app_route_highlights_location(request):
    highlights = search_highlights(request.json['query'])
    return json({ "success": True, "highlights": highlights })

@app.route('/v1/queries/summarize-user', methods = ['POST'])
def app_route_summarize_user(request):
    user = request.json['user']
    answer = summarize_user(user)
    return json({ "success": True, "answer": answer })

@app.route('/v1/queries/contrast-users', methods = ['POST'])
def app_route_contrast_users(request):
    user_one = request.json['user_one']
    statement_one = summarize_user(user_one)
    user_two = request.json['user_two']
    statement_two = summarize_user(user_two)
    answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
    return json({ "success": True, "answer": answer })


# USERS

@app.route('/v1/user/<user_id>', methods = ['GET'])
async def app_route_user(request, user_id):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User).where(User.id == int(user_id)))
        user = query_user.scalar_one_or_none()
        # TODO: figure out how to do these serialize() calls recurisvely within user.serialize()
        user_json = user.serialize() 
    return json({ "success": True, "user": user_json })

@app.route('/v1/users', methods = ['GET'])
async def app_route_users(request):
    session = request.ctx.session
    async with session.begin():
        query_user = await session.execute(sa.select(User))
        users = query_user.scalars()
        user_json = serialize_list(users)
    return json({ "success": True, "users": user_json })


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
 