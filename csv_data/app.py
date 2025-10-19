import logging
from flask import Flask, render_template, request, jsonify
from utils.extractor_v4 import extract_data
from utils.interpreter_v2 import interpret_data

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No JSON data provided'}), 400

    try:
        result = handle_process(json_data)
        return jsonify(result)
    except Exception as e:
        logging.exception("Error in /process endpoint")
        return jsonify({'error': str(e)}), 500

def handle_process(data):
    extracted = extract_data(data)
    interpreted = interpret_data(extracted)
    return interpreted

if __name__ == '__main__':
    app.run(debug=True)
