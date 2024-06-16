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
    return None

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        submissions = load_json('submissions.json')
        if submissions is None:
            return jsonify({"error": "Submissions file not found"}), 404
        return jsonify(submissions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submissions', methods=['POST'])
def add_submission():
    try:
        submission = request.json
        submissions = load_json('submissions.json')
        if submissions is None:
            return jsonify({"error": "Submissions file not found"}), 404
        submissions.append(submission)
        save_json('submissions.json', submissions)
        return jsonify(submission), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submissions/<int:index>', methods=['DELETE'])
def delete_submission(index):
    try:
        submissions = load_json('submissions.json')
        if submissions is None:
            return jsonify({"error": "Submissions file not found"}), 404
        if 0 <= index < len(submissions):
            deleted_submission = submissions.pop(index)
            save_json('submissions.json', submissions)
            return jsonify(deleted_submission), 200
        return jsonify({'error': 'Index out of range'}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    try:
        if request.method == 'POST':
            submission = request.json
            question_data = load_json('questions.json')
            if question_data is None:
                return jsonify({"error": "Questions file not found"}), 404
            if submission['type'] == 'video':
                question_data['questions'].append({
                    "id": len(question_data['questions']) + 1,
                    "type": "video",
                    "content": submission['content'],
                    "questions": submission['questions'],
                    "path": submission['path']
                })
            elif submission['type'] == 'botTalk':
                question_data['questions'].append({
                    "id": len(question_data['questions']) + 1,
                    "type": "botTalk",
                    "phrases": submission['phrases'],
                    "path": submission['path']
                })
            elif submission['type'] == 'pronunciations':
                question_data['questions'].append({
                    "id": len(question_data['questions']) + 1,
                    "type": "pronunciations",
                    "words": submission['words'],
                    "path": submission['path']
                })
            elif submission['type'] == 'speakOutLoud':
                question_data['questions'].append({
                    "id": len(question_data['questions']) + 1,
                    "type": "speakOutLoud",
                    "sentences": submission['sentences'],
                    "path": submission['path']
                })
            save_json('questions.json', question_data)
            return jsonify(submission), 201
        elif request.method == 'GET':
            questions = load_json('questions.json')
            if questions is None:
                return jsonify({"error": "Questions file not found"}), 404
            return jsonify(questions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
