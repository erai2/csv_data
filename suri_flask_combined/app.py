
from flask import Flask, request, jsonify, render_template
import os

# Import DB utilities
from db.db_utils import get_db_connection
from db.init_db_data import initialize_database

# Import inference engine
from infer.infer_engine import infer_from_input

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init-db', methods=['POST'])
def init_db():
    try:
        initialize_database()
        return jsonify({'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def db_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return jsonify({'tables': [table[0] for table in tables]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/infer', methods=['POST'])
def infer():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    try:
        result = infer_from_input(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
