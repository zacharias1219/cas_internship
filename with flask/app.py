from flask import Flask, render_template, request, jsonify, session
import os
from utils import get_answer, text_to_speech, speech_to_text, semantic_similarity
from models.sentence_transformer import SentenceTransformerModel

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the NLP model for semantic similarity
model = SentenceTransformerModel()

# Define interview scenarios, levels, and their respective system prompts
scenarios = {
    "Java Interview": {
        "Beginner": "You are an experienced interviewer conducting a beginner level Java programming interview session with the user. Ask about basic OOP concepts and Java syntax. Prepare {max_questions} questions.",
        "Intermediate": "You are an experienced interviewer conducting an intermediate level Java programming interview session with the user. Ask about advanced OOP concepts and Java libraries. Prepare {max_questions} questions.",
        "Hard": "You are an experienced interviewer conducting a hard level Java programming interview session with the user. Ask about complex design patterns and performance optimization in Java. Prepare {max_questions} questions."
    },
    "Excel Interview": {
        "Beginner": "You are an experienced interviewer conducting a beginner level Excel skills interview session with the user. Ask about basic Excel formulas, data entry, and simple data manipulation. Prepare {max_questions} questions.",
        "Intermediate": "You are an experienced interviewer conducting an intermediate level Excel skills interview session with the user. Ask about advanced Excel formulas, data analysis, and pivot tables. Prepare {max_questions} questions.",
        "Hard": "You are an experienced interviewer conducting a hard level Excel skills interview session with the user. Ask about VBA macros, complex data analysis, and automation in Excel. Prepare {max_questions} questions."
    }
}

content = {
    "Java Interview": {
        "Beginner": "Welcome to the beginner level Java interview. Let's start with your introduction.",
        "Intermediate": "Welcome to the intermediate level Java interview.",
        "Hard": "Welcome to the hard level Java interview."
    },
    "Excel Interview": {
        "Beginner": "Welcome to the beginner level Excel interview. Let's start with your introduction.",
        "Intermediate": "Welcome to the intermediate level Excel interview.",
        "Hard": "Welcome to the hard level Excel interview."
    }
}

levels = ["Beginner", "Intermediate", "Hard"]
EVALUATION_THRESHOLD = 0.4

@app.route('/')
def index():
    return render_template('index.html', scenarios=scenarios, levels=levels)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    scenario = data.get('scenario')
    level = data.get('level')
    user_input = data.get('message')

    # Initialize session variables if they don't exist
    if 'messages' not in session:
        session['messages'] = [{"role": "assistant", "content": content[scenario]["Beginner"]}]
    if 'selected_scenario' not in session:
        session['selected_scenario'] = scenario
    if 'selected_level' not in session:
        session['selected_level'] = level
    if 'answers' not in session:
        session['answers'] = []
    if 'level_progress' not in session:
        session['level_progress'] = {"Java Interview": "Beginner", "Excel Interview": "Beginner"}
    if 'incorrect_attempts' not in session:
        session['incorrect_attempts'] = 0
    if 'max_questions' not in session:
        session['max_questions'] = 5
    if 'current_question' not in session:
        session['current_question'] = 0
    if 'introduction_given' not in session:
        session['introduction_given'] = False
    if 'user_introduction' not in session:
        session['user_introduction'] = ""

    if user_input:
        session['messages'].append({"role": "user", "content": user_input})
        if session['introduction_given']:
            session['answers'].append(user_input)
        else:
            session['user_introduction'] = user_input
            session['introduction_given'] = True

        system_prompt = scenarios[scenario][session['level_progress'][scenario]].format(max_questions=session['max_questions'])
        final_response = get_answer(session['messages'], system_prompt)
        audio_file = text_to_speech(final_response)
        session['messages'].append({"role": "assistant", "content": final_response})

        return jsonify({"response": final_response, "audio": audio_file})

    return jsonify({"response": "Error: No input received."})

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({"status": "reset"})

if __name__ == '__main__':
    app.run(debug=True)
