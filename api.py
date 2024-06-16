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
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {file_path}: {e}")
                return None
    return None

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/submissions', methods=['GET'])
def get_submissions():
    submissions = load_json('submissions.json')
    if submissions is None:
        return jsonify({"error": "Failed to load submissions"}), 500
    return jsonify(submissions)

@app.route('/submissions', methods=['POST'])
def add_submission():
    try:
        submission = request.json
        submissions = load_json('submissions.json')
        if submissions is None:
            submissions = []
        submissions.append(submission)
        save_json('submissions.json', submissions)
        return jsonify(submission), 201
    except Exception as e:
        print(f"Error adding submission: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submissions/<int:index>', methods=['DELETE'])
def delete_submission(index):
    try:
        submissions = load_json('submissions.json')
        if submissions is None:
            return jsonify({"error": "Failed to load submissions"}), 500
        if 0 <= index < len(submissions):
            deleted_submission = submissions.pop(index)
            save_json('submissions.json', submissions)
            return jsonify(deleted_submission), 200
        return jsonify({'error': 'Index out of range'}), 404
    except Exception as e:
        print(f"Error deleting submission: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = load_json('questions.json')
    if questions is None:
        return jsonify({"error": "Failed to load questions"}), 500
    return jsonify(questions)

@app.route('/questions', methods=['POST'])
def add_to_bank():
    try:
        submission = request.json
        question_data = load_json('questions.json')
        if question_data is None:
            question_data = {"questions": []}
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
    except Exception as e:
        print(f"Error adding to bank: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
