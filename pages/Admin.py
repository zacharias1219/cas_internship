import streamlit as st
import json
import os

# Load the question data from a JSON file
def load_questions(path):
    name = f"questions{path}.json"
    if os.path.exists(name):
        with open(name, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"questions": []}
    return {"questions": []}

# Save questions to a JSON file
def save_questions(path, questions):
    name = f"questions{path}.json"
    with open(name, 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)

# Function to add a new question
def add_question(path, question):
    questions = load_questions(path)
    question['id'] = len(questions['questions']) + 1
    questions['questions'].append(question)
    save_questions(path, questions)

# Function to delete a question by ID
def delete_question(path, question_id):
    questions = load_questions(path)
    questions['questions'] = [q for q in questions['questions'] if q['id'] != question_id]
    save_questions(path, questions)

# Function to move a question up in the sequence
def move_question_up(path, index):
    questions = load_questions(path)
    if index > 0:
        questions['questions'][index], questions['questions'][index - 1] = questions['questions'][index - 1], questions['questions'][index]
        save_questions(path, questions)

# Function to move a question down in the sequence
def move_question_down(path, index):
    questions = load_questions(path)
    if index < len(questions['questions']) - 1:
        questions['questions'][index], questions['questions'][index + 1] = questions['questions'][index + 1], questions['questions'][index]
        save_questions(path, questions)

# Admin Page
st.title("Admin Page")

# Add New Question Form
st.sidebar.title("Add New Question")
path = st.sidebar.selectbox("Select the path data that you want to edit", [1, 2], key='path_selector')
question_type = st.sidebar.selectbox("Question Type", ["video", "botTalk", "pronunciations", "speakOutLoud", "textQuiz", "voiceQuiz", "pictureQuiz", "pictureDescription"], key='question_type_selector')

if question_type == "video":
    video_url = st.sidebar.text_input("Video URL")
    question = st.sidebar.text_input("Question")
    correct_answer = st.sidebar.text_input("Correct Answer")
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "video",
            "content": video_url,
            "questions": [{"question": question, "correct_answer": correct_answer}],
            "path": "video"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "botTalk":
    phrase = st.sidebar.text_input("Initial Prompt")
    time_limit = st.sidebar.number_input("Duration (minutes)", min_value=1, max_value=60, value=3)
    additional_info = st.sidebar.text_input("Additional Information")
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "botTalk",
            "phrases": phrase,
            "path": "botTalk",
            "time": time_limit,
            "additional": additional_info
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "pronunciations":
    words = st.sidebar.text_area("Words (comma separated)")
    if st.sidebar.button("Add Question"):
        words_list = [word.strip() for word in words.split(',')]
        new_question = {
            "type": "pronunciations",
            "words": words_list,
            "path": "pronunciations"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "speakOutLoud":
    sentences = st.sidebar.text_area("Sentences (comma separated)")
    if st.sidebar.button("Add Question"):
        sentences_list = [sentence.strip() for sentence in sentences.split(',')]
        new_question = {
            "type": "speakOutLoud",
            "sentences": sentences_list,
            "path": "speakOutLoud"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "textQuiz":
    questions = []
    for i in range(1, 3):
        question = st.sidebar.text_input(f"Question {i}")
        answer = st.sidebar.text_input(f"Answer {i}")
        hint = st.sidebar.text_input(f"Hint {i}")
        questions.append({"question": question, "correct_answer": answer, "hint": hint})
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "textQuiz",
            "questions": questions,
            "path": "textQuiz"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "voiceQuiz":
    questions = []
    for i in range(1, 3):
        question = st.sidebar.text_input(f"Question {i}")
        answer = st.sidebar.text_input(f"Answer {i}")
        hint = st.sidebar.text_input(f"Hint {i}")
        questions.append({"question": question, "correct_answer": answer, "hint": hint})
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "voiceQuiz",
            "questions": questions,
            "path": "voiceQuiz"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "pictureQuiz":
    image_url = st.sidebar.text_input("Image URL")
    questions = []
    for i in range(1, 3):
        question = st.sidebar.text_input(f"Question {i}")
        answer = st.sidebar.text_input(f"Answer {i}")
        hint = st.sidebar.text_input(f"Hint {i}")
        questions.append({"question": question, "correct_answer": answer, "hint": hint})
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "pictureQuiz",
            "image_url": image_url,
            "questions": questions,
            "path": "pictureQuiz"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "pictureDescription":
    image_url = st.sidebar.text_input("Image URL")
    questions = []
    for i in range(1, 3):
        question = st.sidebar.text_input(f"Question {i}")
        questions.append({"question": question})
    if st.sidebar.button("Add Question"):
        new_question = {
            "type": "pictureDescription",
            "image_url": image_url,
            "questions": questions,
            "path": "pictureDescription"
        }
        add_question(path, new_question)
        st.sidebar.success("Question added successfully!")

# Display Current Sequence
st.header("Current Sequence")
questions = load_questions(path)["questions"]

for index, question in enumerate(questions):
    st.write(f"{index + 1}. {question['type']} - {question.get('content', 'N/A')}")
    st.write(question.get('phrases', question.get('words', question.get('sentences', 'N/A'))))
    st.write(question.get('questions', 'N/A'))
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(f"Delete {index + 1}", key=f"delete_{index}"):
            delete_question(path, question['id'])
            st.rerun()
    with col2:
        if st.button(f"Move Up {index + 1}", key=f"move_up_{index}"):
            move_question_up(path, index)
            st.rerun()
    with col3:
        if st.button(f"Move Down {index + 1}", key=f"move_down_{index}"):
            move_question_down(path, index)
            st.rerun()
