import streamlit as st
import json
import os

# Load the submission data from JSON file
def load_questions():
    if os.path.exists('questions.json'):
        with open('questions.json', 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"questions": []}
    return {"questions": []}

# Save questions to JSON file
def save_questions(questions):
    with open('questions.json', 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)

# Function to add a new question
def add_question(question):
    questions = load_questions()
    question['id'] = len(questions['questions']) + 1
    questions['questions'].append(question)
    save_questions(questions)

# Function to delete a question by ID
def delete_question(question_id):
    questions = load_questions()
    questions['questions'] = [q for q in questions['questions'] if q['id'] != question_id]
    save_questions(questions)

# Function to move a question up in the sequence
def move_question_up(index):
    questions = load_questions()
    if index > 0:
        questions['questions'][index], questions['questions'][index - 1] = questions['questions'][index - 1], questions['questions'][index]
        save_questions(questions)

# Function to move a question down in the sequence
def move_question_down(index):
    questions = load_questions()
    if index < len(questions['questions']) - 1:
        questions['questions'][index], questions['questions'][index + 1] = questions['questions'][index + 1], questions['questions'][index]
        save_questions(questions)

# Admin Page
st.title("Admin Page")

# Add New Question Form
st.sidebar.title("Add New Question")
question_type = st.sidebar.selectbox("Question Type", ["video", "botTalk", "speakOutLoud"])

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
        add_question(new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "botTalk":
    phrases = st.sidebar.text_area("Phrases (comma separated) (Only Two)")
    if st.sidebar.button("Add Question"):
        phrases_list = [phrase.strip() for phrase in phrases.split(',')]
        new_question = {
            "type": "botTalk",
            "phrases": phrases_list,
            "path": "botTalk"
        }
        add_question(new_question)
        st.sidebar.success("Question added successfully!")

elif question_type == "speakOutLoud":
    sentences = st.sidebar.text_area("Sentences (comma separated) (Only Two)")
    if st.sidebar.button("Add Question"):
        sentences_list = [sentence.strip() for sentence in sentences.split(',')]
        new_question = {
            "type": "speakOutLoud",
            "sentences": sentences_list,
            "path": "speakOutLoud"
        }
        add_question(new_question)
        st.sidebar.success("Question added successfully!")

# Display Current Sequence
st.header("Current Sequence")
questions = load_questions()["questions"]

for index, question in enumerate(questions):
    st.write(f"{index + 1}. {question['type']} - {question.get('content', 'N/A')}")
    st.write(question.get('phrases', question.get('sentences', 'N/A')))
    st.write(question.get('questions', 'N/A'))
    
    if st.button(f"Delete {index + 1}"):
        delete_question(question['id'])
        st.experimental_rerun()
    
    if st.button(f"Move Up {index + 1}"):
        move_question_up(index)
        st.experimental_rerun()
    
    if st.button(f"Move Down {index + 1}"):
        move_question_down(index)
        st.experimental_rerun()
