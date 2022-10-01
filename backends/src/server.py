from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

from gideon_utils import get_file_path, get_documents_json, get_highlights_json, without_keys
from index_audio import index_audio
from index_highlight import index_highlight
from index_pdf import index_pdf
from queries.contrast_two_user_statements import contrast_two_user_statements
from queries.question_answer import question_answer
from queries.search_for_locations import search_for_locations, search_for_locations_by_vector
from queries.search_highlights import search_highlights
from queries.summarize_user import summarize_user

# INIT
app = Sanic("API")
CORS(app)



# DOCUMENTS

@app.route('/documents/indexed', methods = ['GET'])
async def endpoint_documents(request):
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

@app.route('/documents/index/pdf', methods = ['POST'])
async def endpoint_documents_intake_pdf(request):
    # --- save file
    file = request.files['file']
    file.save(get_file_path("../documents/{filename}".format(filename=file.filename)))
    # --- run processing
    index_pdf(file.filename, "discovery")
    # --- respond saying we got the file, but continue on w/ processing
    return json({ "success": True })

@app.route('/documents/index/audio', methods = ['POST'])
async def endpoint_documents_intake_audio(request):
    # --- save file
    file = request.files['file']
    file.save(get_file_path("../documents/{filename}".format(filename=file.filename)))
    # --- run processing
    index_audio(file.filename)
    # --- respond saying we got the file, but continue on w/ processing
    return json({ "success": True })


# HIGHLIGHTS

@app.route('/highlights', methods = ['GET'])
async def endpoint_highlights(request):
    highlights = get_highlights_json()
    return json({ "success": True, "highlights": highlights })

@app.route('/highlights', methods = ['POST'])
async def endpoint_highlight_create(request):
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

@app.route('/queries/question-answer', methods = ['POST'])
async def endpoint_question_answer(request):
    answer = question_answer(request.json['question'], request.json['index_type'])
    return json({ "success": True, "answer": answer })

@app.route('/queries/query-info-locations', methods = ['POST'])
async def endpoint_query_info_locations(request):
    locations = search_for_locations(request.json['query'])
    return json({ "success": True, "locations": locations })

@app.route('/queries/vector-info-locations', methods = ['POST'])
async def endpoint_vector_info_locations(request):
    locations = search_for_locations_by_vector(request.json['vector'])
    return json({ "success": True, "locations": locations })

@app.route('/queries/highlights-query', methods = ['POST'])
async def endpoint_highlights_location(request):
    highlights = search_highlights(request.json['query'])
    return json({ "success": True, "highlights": highlights })

@app.route('/queries/summarize-user', methods = ['POST'])
async def endpoint_summarize_user(request):
    user = request.json['user']
    answer = summarize_user(user)
    return json({ "success": True, "answer": answer })

@app.route('/queries/contrast-users', methods = ['POST'])
async def endpoint_contrast_users(request):
    user_one = request.json['user_one']
    statement_one = summarize_user(user_one)
    user_two = request.json['user_two']
    statement_two = summarize_user(user_two)
    answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
    return json({ "success": True, "answer": answer })


# RUN
if __name__ == "__main__":
    # TODO: recognize env var for auto_reload so we only have it in local
    app.run(host='0.0.0.0', port=3000, access_log=False, auto_reload=True)
 