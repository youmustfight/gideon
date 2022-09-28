from flask import Flask, jsonify, request
from flask_cors import CORS

from gideon_utils import get_file_path, get_documents_json, without_keys
from index_audio import index_audio
from index_pdf import index_pdf
from question_answer import question_answer
from search_for_location import search_for_location

app = Flask(__name__)
CORS(app)

# ENDPOINTS
@app.route('/documents/indexed', methods = ['GET'])
def endpoint_documents():
    def reduced_json(j):
        return without_keys(j, [
            'document_text_vectors',
            'document_text_vectors_by_minute',
            'document_text_vectors_by_paragraph',
            'document_text_vectors_by_page',
        ])
    documents = get_documents_json()
    documents = list(map(reduced_json, documents)) # clear doc vectors
    return jsonify({ "success": True, "documents": documents })

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

@app.route('/question-answer', methods = ['POST'])
def endpoint_question_answer():
    json = request.get_json()
    answer = question_answer(json['question'], json['index_type'])
    return jsonify({ "success": True, "answer": answer })

@app.route('/question-info-location', methods = ['POST'])
def endpoint_question_info_location():
    json = request.get_json()
    locations = search_for_location(json['question'])
    return jsonify({ "success": True, "locations": locations })


# RUN
app.run(host='0.0.0.0', port=3000)
