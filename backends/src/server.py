from contextvars import ContextVar
import pinecone
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, selectinload, subqueryload, sessionmaker

import env
from files.file_utils import get_file_path, write_file
from indexers.index_audio import index_audio
from indexers.index_highlight import index_highlight
from indexers.index_pdf import index_pdf
from indexers.index_vectors import index_vectors
from indexers.index_image import index_image
from dbs.sa_models import serialize_list, Case, Document, DocumentContent, Embedding, File, User
from queries.contrast_two_user_statements import contrast_two_user_statements
from queries.question_answer import question_answer
from queries.search_for_locations_across_text import search_for_locations_across_text
from queries.search_for_locations_across_image import search_for_locations_across_image
from queries.search_highlights import search_highlights
from queries.summarize_user import summarize_user


# INIT
app = Sanic("api")
app.config['RESPONSE_TIMEOUT'] = 60 * 30 # HACK: until we move pdf processing outside the api endpoints, disallowing 503 timeout responses now


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
    return json({ "success": True, "user": user.serialize() })


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
@app.route('/v1/document/<document_id>', methods = ['GET'])
async def app_route_document_get(request, document_id):
    session = request.ctx.session
    async with session.begin():
        query_document = await session.execute(
            sa.select(Document)
                .options(
                    selectinload(Document.content),
                    selectinload(Document.files),
                )
                .where(Document.id == int(document_id))
        )
        document = query_document.scalars().first()
        # TODO: figure out how to more elegantly pull off serialized properties
        document_json = document.serialize()
        document_json['content'] = serialize_list(document.content)
        document_json['files'] = serialize_list(document.files)
    return json({ "success": True, "document": document_json })

@app.route('/v1/document/<document_id>', methods = ['DELETE'])
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
            index_documents_clip = pinecone.Index("documents-clip")
            index_documents_clip.delete(ids=embeddings_ids_strs)
            index_documents_text = pinecone.Index("documents-text")
            index_documents_text.delete(ids=embeddings_ids_strs)
            index_documents_sentences = pinecone.Index("documents-sentences")
            index_documents_sentences.delete(ids=embeddings_ids_strs)
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
    return json({ "success": True })

@app.route('/v1/documents', methods = ['GET'])
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
    return json({ "success": True, "documents": documents_json })

@app.route('/v1/documents/index/pdf', methods = ['POST'])
async def app_route_documents_index_pdf(request):
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/pdf/embeddings
        document_id = await index_pdf(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ "success": True })

@app.route('/v1/documents/index/image', methods = ['POST'])
async def app_route_documents_index_image(request):
    session = request.ctx.session
    async with session.begin():
        pyfile = request.files['file'][0]
        # --- process file/embeddings
        document_id = await index_image(session=session, pyfile=pyfile)
        # --- queue indexing
        await index_vectors(session=session, document_id=document_id)
    return json({ "success": True })

# @app.route('/v1/documents/index/audio', methods = ['POST'])
# async def app_route_documents_index_audio(request): 
#     session = request.ctx.session
#     async with session.begin():
#         pyfile = request.files['file'][0]
#         write_file(get_file_path("../documents/{filename}".format(filename=pyfile.name)), pyfile.body)
#         index_audio(session=session, filename=pyfile.name)
#     return json({ "success": True })


# HIGHLIGHTS
@app.route('/v1/highlights', methods = ['GET'])
def app_route_highlights(request):
    highlights = [] # get_highlights_json()
    return json({ "success": True, "highlights": highlights })

# @app.route('/v1/highlights', methods = ['POST'])
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
#     return json({ "success": True })


# INDEXES
@app.route('/v1/index/<index_name>', methods = ['DELETE'])
def app_route_index_delete(request, index_name):
    index_to_clear = pinecone.Index(index_name)
    index_to_clear.delete(deleteAll=True) # just deletes all vectors
    return json({ "success": True })


# QUERIES
@app.route('/v1/queries/document-query', methods = ['POST'])
async def app_route_question_answer(request):
    session = request.ctx.session
    async with session.begin():
        answer = await question_answer(session, request.json['question'])
    return json({ "success": True, "answer": answer })

@app.route('/v1/queries/documents-locations', methods = ['POST'])
async def app_route_query_info_locations(request):
    session = request.ctx.session
    async with session.begin():
        locations_across_text = await search_for_locations_across_text(session, request.json['query'])
        def serialize_location(location):
            return dict(
                document=location['document'].serialize(),
                document_content=location['document_content'].serialize(),
                score=location['score']
            )
        locations_across_text_serialized = list(map(serialize_location, locations_across_text))
        # TODO: re-instate gpt3+clip
        # locations_across_image = search_for_locations_across_image(request.json['query'])
        # locations = locations_across_text + locations_across_image
    return json({ "success": True, "locations": locations_across_text_serialized })

# @app.route('/v1/queries/highlights-query', methods = ['POST'])
# def app_route_highlights_location(request):
#     # TODO: refactor
#     highlights = search_highlights(request.json['query'])
#     return json({ "success": True, "highlights": highlights })

# @app.route('/v1/queries/summarize-user', methods = ['POST'])
# def app_route_summarize_user(request):
#     user = request.json['user']
#     answer = summarize_user(user)
#     return json({ "success": True, "answer": answer })

# @app.route('/v1/queries/contrast-users', methods = ['POST'])
# def app_route_contrast_users(request):
#     user_one = request.json['user_one']
#     statement_one = summarize_user(user_one)
#     user_two = request.json['user_two']
#     statement_two = summarize_user(user_two)
#     answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
#     return json({ "success": True, "answer": answer })


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
 