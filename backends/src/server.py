from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from tortoise.contrib.sanic import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from gideon_utils import get_file_path, get_documents_json, get_highlights_json, without_keys, write_file
from indexers.index_audio import index_audio
from indexers.index_highlight import index_highlight
from indexers.index_pdf import index_pdf
from indexers.index_image import index_image
from models import Users
from orm import TORTOISE_ORM
from queries.contrast_two_user_statements import contrast_two_user_statements
from queries.question_answer import question_answer
from queries.search_for_locations_across_text import search_for_locations_across_text
from queries.search_for_locations_across_image import search_for_locations_across_image
from queries.search_highlights import search_highlights
from queries.summarize_user import summarize_user



# INIT
app = Sanic("api")
CORS(app)


# DOCUMENTS
# TODO: safer file uploading w/ async: https://stackoverflow.com/questions/48930245/how-to-perform-file-upload-in-sanic

@app.route('/documents/indexed', methods = ['GET'])
def app_route_documents(request):
    def reduced_json(j):
        return without_keys(j, [
            'document_text_vectors',
            'document_text_vectors_by_minute',
            'document_text_vectors_by_paragraph',
            'document_text_vectors_by_page',
            # 'document_text_vectors_by_sentence',
        ])
        # Keep sentence vectors for frontend note tagging
    documents = get_documents_json()
    documents = list(map(reduced_json, documents)) # clear doc vectors
    return json({ "success": True, "documents": documents })

@app.route('/documents/index/audio', methods = ['POST'])
def app_route_documents_index_audio(request):
    # --- save file TODO: multiple files
    file = request.files['file'][0]
    file.save(get_file_path("../documents/{filename}".format(filename=file.name)))
    # await async_write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
    # --- run processing
    index_audio(file.name)
    # --- respond
    return json({ "success": True })

@app.route('/documents/index/image', methods = ['POST'])
async def app_route_documents_index_image(request):
    # --- save file TODO: multiple files
    file = request.files['file'][0]
    write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
    # await async_write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
    # --- run processing
    await index_image(file.name)
    # --- respond
    return json({ "success": True })

@app.route('/documents/index/pdf', methods = ['POST'])
def app_route_documents_index_pdf(request):
    # --- save file TODO: multiple files
    file = request.files['file'][0]
    file.save(get_file_path("../documents/{filename}".format(filename=file.name)))
    # await async_write_file(get_file_path("../documents/{filename}".format(filename=file.name)), file.body)
    # --- run processing
    index_pdf(file.name, "discovery")
    # --- respond
    return json({ "success": True })


# HIGHLIGHTS

@app.route('/highlights', methods = ['GET'])
def app_route_highlights(request):
    highlights = get_highlights_json()
    return json({ "success": True, "highlights": highlights })

@app.route('/highlights', methods = ['POST'])
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

@app.route('/queries/question-answer', methods = ['POST'])
def app_route_question_answer(request):
    answer = question_answer(request.json['question'], request.json['index_type'])
    return json({ "success": True, "answer": answer })

@app.route('/queries/query-info-locations', methods = ['POST'])
def app_route_query_info_locations(request):
    locations_across_text = search_for_locations_across_text(request.json['query'])
    locations_across_image = search_for_locations_across_image(request.json['query'])
    # TODO: find a way to normalize scoring of GPT3 + CLIP
    locations = locations_across_text + locations_across_image
    return json({ "success": True, "locations": locations })

@app.route('/queries/highlights-query', methods = ['POST'])
def app_route_highlights_location(request):
    highlights = search_highlights(request.json['query'])
    return json({ "success": True, "highlights": highlights })

@app.route('/queries/summarize-user', methods = ['POST'])
def app_route_summarize_user(request):
    user = request.json['user']
    answer = summarize_user(user)
    return json({ "success": True, "answer": answer })

@app.route('/queries/contrast-users', methods = ['POST'])
def app_route_contrast_users(request):
    user_one = request.json['user_one']
    statement_one = summarize_user(user_one)
    user_two = request.json['user_two']
    statement_two = summarize_user(user_two)
    answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
    return json({ "success": True, "answer": answer })


# USERS
# --- mostly for testing out migrations/models/serialized responses

@app.route('/users', methods = ['GET'])
async def app_route_users(request):
    users = await Users.all().values() # did values() to get dicts since class/models can't be serialized by default w/ sanic/tortise
    return json({ "success": True, "users": users })



# RUN
# --- ORM (https://tortoise-orm.readthedocs.io/en/latest/contrib/sanic.html#contrib-sanic)
register_tortoise(
    app,
    db_url=TORTOISE_ORM['connections']['default'],
    generate_schemas=True,
    modules={"models": ["models"]}
)
# --- SANIC SERVER WORKERS
if __name__ == "__main__":
    # TODO: recognize env var for auto_reload so we only have it in local
    # TODO: maybe use this forever serve for prod https://github.com/sanic-org/sanic/blob/main/examples/run_async.py
    app.run(host='0.0.0.0', port=3000, access_log=False, auto_reload=True)
 