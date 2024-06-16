from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Initialize data
if not os.path.exists('submissions.json'):
    with open('submissions.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('questions.json'):
    with open('questions.json', 'w') as f:
        json.dump({"questions": []}, f)

# Load data from JSON files
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        submission = request.json
        submissions = load_json('submissions.json')
        submissions.append(submission)
        save_json('submissions.json', submissions)
        return jsonify({"message": "Submission received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
