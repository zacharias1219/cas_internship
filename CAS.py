import json
import os
import random
import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from sentence_transformers import SentenceTransformer, util

st.set_page_config(
    page_title="Interview Bot",
    layout="wide",
    page_icon="💬",
    initial_sidebar_state="collapsed",
)

# Float feature initialization
float_init()

# Initialize the NLP model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load questions and ideal answers from the JSON file
with open('questions.json', 'r') as file:
    questions_data = json.load(file)

# Function to get questions based on scenario and level
def get_questions(scenario, level, max_questions):
    questions = questions_data[scenario][level]
    return random.sample(questions, min(max_questions, len(questions)))

# Define levels
levels = ["Beginner", "Intermediate", "Hard"]

EVALUATION_THRESHOLD = 0.1  # Set the evaluation metric threshold here

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to the interview. Let's start with your introduction."}]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Java Interview"
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = "Beginner"
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "level_progress" not in st.session_state:
        st.session_state.level_progress = {scenario: "Beginner" for scenario in questions_data.keys()}
    if "incorrect_attempts" not in st.session_state:
        st.session_state.incorrect_attempts = 0
    if "max_questions" not in st.session_state:
        st.session_state.max_questions = 5  # Default maximum number of questions
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "introduction_given" not in st.session_state:
        st.session_state.introduction_given = False
    if "user_introduction" not in st.session_state:
        st.session_state.user_introduction = ""
    if "current_questions" not in st.session_state:
        st.session_state.current_questions = []

initialize_session_state()

st.title("Interview Bot 🤖")

# Progress Bar
progress = st.progress(0)
progress_percent = (st.session_state.current_question / st.session_state.max_questions)
progress.progress(progress_percent)

# Function to determine if the next level is unlocked
def unlock_next_level(current_level):
    if current_level == "Beginner":
        return "Intermediate"
    elif current_level == "Intermediate":
        return "Hard"
    else:
        return None

# Use columns to place the dropdown, audio recorder, end session button, and slider side by side
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col1:
    # Scenario selection
    selected_scenario = st.selectbox(
        "Choose an interview",
        list(questions_data.keys()),
        index=list(questions_data.keys()).index(st.session_state.selected_scenario)
    )

    current_level = st.session_state.level_progress[selected_scenario]
    st.write(f"Current level: {current_level}")

with col2:
    # Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = audio_recorder()

with col3:
    # End session button
    if st.button("End Session"):
        st.session_state.clear()
        initialize_session_state()
        st.experimental_rerun()

with col4:
    # Maximum number of questions slider
    st.session_state.max_questions = st.slider(
        "Max Questions",
        min_value=2,
        max_value=10,
        value=5
    )

# Update the session state if the scenario changes
if selected_scenario != st.session_state.selected_scenario:
    st.session_state.selected_scenario = selected_scenario
    st.session_state.selected_level = "Beginner"
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to the interview. Let's start with your introduction."}]
    st.session_state.answers = []
    st.session_state.incorrect_attempts = 0
    st.session_state.current_question = 0
    st.session_state.introduction_given = False
    st.session_state.user_introduction = ""
    st.session_state.current_questions = get_questions(selected_scenario, st.session_state.selected_level, st.session_state.max_questions)

# Function to get the next question
def get_next_question():
    if st.session_state.current_question < len(st.session_state.current_questions):
        return st.session_state.current_questions[st.session_state.current_question]
    else:
        return None

next_question = get_next_question()

if next_question:
    st.session_state.messages.append({"role": "assistant", "content": next_question["question"]})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            if st.session_state.introduction_given:
                st.session_state.answers.append(transcript)  # Store the user's answer
            else:
                st.session_state.user_introduction = transcript  # Save the user's introduction
                st.session_state.introduction_given = True
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

if st.session_state.messages[-1]["role"] != "assistant" and st.session_state.introduction_given:
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            final_response = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):    
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

# Evaluation function
def evaluate_answers(user_answers):
    scores = []
    for user_answer, assistant_msg in zip(user_answers, st.session_state.messages):
        if assistant_msg["role"] == "assistant":
            expected_answer = assistant_msg["content"]
            score = semantic_similarity(user_answer, expected_answer)
            scores.append(score)
    return scores

# Handle answer function
def handle_answer(user_answer):
    expected_answer = st.session_state.messages[-1]["content"]
    user_answer_clean = user_answer.strip().lower()
    expected_answer_clean = expected_answer.strip().lower()

    if not user_answer_clean or "explain" in user_answer_clean or "again" in user_answer_clean:
        return "not an answer", 0.0
    
    score = semantic_similarity(user_answer_clean, expected_answer_clean)
    if score >= EVALUATION_THRESHOLD:
        st.session_state.incorrect_attempts = 0
        return "correct", score
    else:
        st.session_state.incorrect_attempts += 1
        if st.session_state.incorrect_attempts == 3:
            return "explain and move on", score
        elif st.session_state.incorrect_attempts == 2:
            return "explain briefly", score
        else:
            return "incorrect", score

# Function to calculate semantic similarity
def semantic_similarity(user_answer, expected_answer):
    embeddings1 = model.encode(user_answer, convert_to_tensor=True)
    embeddings2 = model.encode(expected_answer, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
    return cosine_scores.item()

def process_answer():
    user_answer = st.session_state.answers[-1]
    result, score = handle_answer(user_answer)
    if result == "correct":
        st.write(f"Correct! (Score: {score:.2f}) Moving to the next question.")
        st.session_state.current_question += 1
    elif result == "incorrect":
        st.write(f"That's not quite right. (Score: {score:.2f}) Let's try again.")
    elif result == "explain briefly":
        st.write(f"That's not quite right. Here's a brief explanation: {st.session_state.messages[-1]['content']}")
    elif result == "explain and move on":
        st.write(f"That's not quite right. Here's a detailed explanation: {st.session_state.messages[-1]['content']}")
        st.session_state.current_question += 1
        st.session_state.incorrect_attempts = 0
    elif result == "not an answer":
        st.write("Please provide a relevant answer.")
    
    progress_percent = (st.session_state.current_question / st.session_state.max_questions)
    progress.progress(progress_percent)

    if st.session_state.current_question >= st.session_state.max_questions:
        st.write("Interview complete. Congratulations!")
        evaluate_session()

def evaluate_session():
    user_answers = st.session_state.answers[:st.session_state.max_questions]
    scores = evaluate_answers(user_answers)
    if all(score >= EVALUATION_THRESHOLD for score in scores):
        next_level = unlock_next_level(st.session_state.level_progress[selected_scenario])
        if next_level:
            st.session_state.level_progress[selected_scenario] = next_level
            st.session_state.selected_level = next_level
            st.session_state.messages = [
                {"role": "assistant", "content": f"Interview complete. You are moving to the {next_level} level."},
                {"role": "user", "content": st.session_state.user_introduction}
            ]
            st.session_state.answers = [st.session_state.user_introduction]
            st.session_state.incorrect_attempts = 0
            st.session_state.current_question = 0
            st.experimental_rerun()
        else:
            st.write("You have completed all levels. Congratulations!")
    else:
        st.write("You did not pass. Please try again from the beginner level.")
        st.session_state.level_progress[selected_scenario] = "Beginner"
        st.session_state.selected_level = "Beginner"
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to the interview. Let's start with your introduction."}]
        st.session_state.answers = []
        st.session_state.incorrect_attempts = 0
        st.session_state.current_question = 0
        st.session_state.introduction_given = False
        st.session_state.user_introduction = ""

if st.session_state.introduction_given and len(st.session_state.answers) > 0:
    process_answer()

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
