from flask import Flask, jsonify, request
from flask_cors import CORS

from gideon_utils import get_file_path, get_documents_json, get_highlights_json, without_keys
from index_audio import index_audio
from index_highlight import index_highlight
from index_pdf import index_pdf
from queries.contrast_two_user_statements import contrast_two_user_statements
from queries.question_answer import question_answer
from queries.search_for_location import search_for_location
from queries.search_highlights import search_highlights
from queries.summarize_user import summarize_user

app = Flask(__name__)
CORS(app)


# DOCUMENTS

@app.route('/documents/indexed', methods = ['GET'])
def endpoint_documents():
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
    return jsonify({ "success": True, "documents": documents })


# DOCUMENT INDEXING

@app.route('/documents/index/pdf', methods = ['POST'])
def endpoint_documents_intake_pdf():
    # --- save file
    file = request.files['file']
    file.save(get_file_path("../documents/{filename}".format(filename=file.filename)))
    # --- run processing
    index_pdf(file.filename, "discovery")
    # --- respond saying we got the file, but continue on w/ processing
    return jsonify({ "success": True })

@app.route('/documents/index/audio', methods = ['POST'])
def endpoint_documents_intake_audio():
    # --- save file
    file = request.files['file']
    file.save(get_file_path("../documents/{filename}".format(filename=file.filename)))
    # --- run processing
    index_audio(file.filename)
    # --- respond saying we got the file, but continue on w/ processing
    return jsonify({ "success": True })


# HIGHLIGHTS

@app.route('/highlights', methods = ['GET'])
def endpoint_highlights():
    highlights = get_highlights_json()
    return jsonify({ "success": True, "highlights": highlights })

@app.route('/highlights', methods = ['POST'])
def endpoint_highlight_create():
    json = request.get_json()
    highlight = json['highlight']
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
    return jsonify({ "success": True })


# QUERIES

@app.route('/queries/question-answer', methods = ['POST'])
def endpoint_question_answer():
    json = request.get_json()
    answer = question_answer(json['question'], json['index_type'])
    return jsonify({ "success": True, "answer": answer })

@app.route('/queries/question-info-location', methods = ['POST'])
def endpoint_question_info_location():
    json = request.get_json()
    locations = search_for_location(json['question'])
    return jsonify({ "success": True, "locations": locations })

@app.route('/queries/highlights-query', methods = ['POST'])
def endpoint_highlights_location():
    json = request.get_json()
    highlights = search_highlights(json['query'])
    return jsonify({ "success": True, "highlights": highlights })

@app.route('/queries/summarize-user', methods = ['POST'])
def endpoint_summarize_user():
    json = request.get_json()
    user = json['user']
    answer = summarize_user(user)
    return jsonify({ "success": True, "answer": answer })

@app.route('/queries/contrast-users', methods = ['POST'])
def endpoint_contrast_users():
    json = request.get_json()
    user_one = json['user_one']
    statement_one = summarize_user(user_one)
    user_two = json['user_two']
    statement_two = summarize_user(user_two)
    answer = contrast_two_user_statements(user_one, statement_one, user_two, statement_two)
    return jsonify({ "success": True, "answer": answer })

# RUN
app.run(host='0.0.0.0', port=3000)
