import streamlit as st
import json
import random
import os
import tempfile
import string
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from utils import speech_to_text
from streamlit_float import float_init
from fuzzywuzzy import fuzz

# Load environment variables
load_dotenv()

# Float feature initialization
float_init()

# Load the question data from JSON files
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as file:
            return json.load(file)
    return {"questions": []}

question_data = load_json('questions.json')

# Helper function to normalize text by removing punctuation and extra whitespace
def normalize_text(text):
    translator = str.maketrans('', '', string.punctuation)
    normalized = ' '.join(text.lower().translate(translator).split())
    return normalized

# Function to check similarity
def is_similar(text1, text2, threshold=90):
    return fuzz.ratio(text1, text2) >= threshold

# Function to check if a phrase is contained within the response
def contains_phrase(response, phrase):
    return phrase.lower() in response.lower()

# Function to handle audio response
def handle_audio_response(prompt, correct_answer, key, check_partial=False):
    audio_data = audio_recorder(f"Record your response:", key=key)
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_file.write(audio_data)
            audio_file_path = audio_file.name
        
        transcription = speech_to_text(audio_file_path)
        normalized_transcription = normalize_text(transcription)
        normalized_correct_answer = normalize_text(correct_answer)

        if check_partial:
            if contains_phrase(normalized_transcription, normalized_correct_answer):
                st.success("Correct answer!")
                st.session_state[f"audio_correct_{key}"] = True
            else:
                st.error(f"Incorrect answer, you said '{transcription}', please try again.")
                st.session_state[f"audio_correct_{key}"] = False
        else:
            if is_similar(normalized_transcription, normalized_correct_answer):
                st.success("Correct answer!")
                st.session_state[f"audio_correct_{key}"] = True
            else:
                st.error(f"Incorrect answer, you said '{transcription}', please try again.")
                st.session_state[f"audio_correct_{key}"] = False

# Function to handle text response
def handle_text_response(prompt, correct_answer, key, check_partial=False):
    user_response = st.text_input("Your answer", key=key)
    if st.button("Submit", key=f"submit_{key}"):
        normalized_user_response = normalize_text(user_response)
        normalized_correct_answer = normalize_text(correct_answer)

        if check_partial:
            if contains_phrase(normalized_user_response, normalized_correct_answer):
                st.success("Correct answer!")
                st.session_state[f"text_correct_{key}"] = True
            else:
                st.error(f"Incorrect answer, you said '{user_response}', please try again.")
                st.session_state[f"text_correct_{key}"] = False
        else:
            if is_similar(normalized_user_response, normalized_correct_answer):
                st.success("Correct answer!")
                st.session_state[f"text_correct_{key}"] = True
            else:
                st.error(f"Incorrect answer, you said '{user_response}', please try again.")
                st.session_state[f"text_correct_{key}"] = False

# Template functions
def video_template(data):
    st.write("Video")
    st.video(data['content'])
    for i, question in enumerate(data['questions']):
        st.write(question['question'])
        handle_audio_response(question['question'], question['correct_answer'], key=f"video_audio_{data['id']}_{i}")
        handle_text_response(question['question'], question['correct_answer'], key=f"video_text_{data['id']}_{i}")

def bot_talk_template(data):
    st.write("Bot Talk")
    responses = {
        "Hello! How are you?": "I'm doing well.",
        "What is your name?": "My name is",
        "Good morning!": "Good morning!",
        "Where are you from?": "I am from"
    }
    for i, phrase in enumerate(data['phrases']):
        st.write(phrase)
        hint = responses[phrase]
        st.write(f"Say: {hint}")
        check_partial = phrase in ["What is your name?", "Where are you from?"]
        handle_audio_response(phrase, hint, key=f"botTalk_audio_{data['id']}_{i}", check_partial=check_partial)
        handle_text_response(phrase, hint, key=f"botTalk_text_{data['id']}_{i}", check_partial=check_partial)

def pronunciations_template(data):
    st.write("Pronunciations")
    for i, word in enumerate(data['words']):
        st.write(word)
        handle_audio_response(word, word, key=f"pronunciations_audio_{data['id']}_{i}")
        handle_text_response(word, word, key=f"pronunciations_text_{data['id']}_{i}")

def speak_out_loud_template(data):
    st.write("Speak Out Loud")
    for i, sentence in enumerate(data['sentences']):
        st.write(sentence)
        handle_audio_response(sentence, sentence, key=f"speakOutLoud_audio_{data['id']}_{i}")
        handle_text_response(sentence, sentence, key=f"speakOutLoud_text_{data['id']}_{i}")

# Function to select one random question from each path type
def select_random_questions():
    path_types = ['video', 'botTalk', 'pronunciations', 'speakOutLoud']
    selected_questions = []

    for path_type in path_types:
        filtered_questions = [q for q in question_data['questions'] if q['path'] == path_type]
        if filtered_questions:
            selected_questions.append(random.choice(filtered_questions))

    random.shuffle(selected_questions)
    return selected_questions

# Initialize session state
def initialize_session_state():
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    if 'current_path' not in st.session_state:
        st.session_state.current_path = question_data['questions']
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'next_clicked' not in st.session_state:
        st.session_state.next_clicked = False

initialize_session_state()

def next_step():
    st.session_state.next_clicked = True
    st.session_state.current_step += 1
    if st.session_state.current_step >= len(st.session_state.current_path):
        st.session_state.current_section += 1
        st.session_state.current_step = 0
        if st.session_state.current_section < 12:
            st.session_state.current_path = question_data['questions']

def render_step(step):
    step_type = step['type']
    if step_type == 'video':
        video_template(step)
    elif step_type == 'botTalk':
        bot_talk_template(step)
    elif step_type == 'pronunciations':
        pronunciations_template(step)
    elif step_type == 'speakOutLoud':
        speak_out_loud_template(step)

st.title("Interactive Learning Path")

current_path = st.session_state.current_path
current_step_index = st.session_state.current_step
steps = current_path

if current_step_index < len(steps):
    step = steps[current_step_index]
    render_step(step)

    step_id = step['id']
    question_count = len(step.get('questions', [])) + len(step.get('phrases', [])) + len(step.get('words', [])) + len(step.get('sentences', []))

    all_questions_correct = all(
        st.session_state.get(f"audio_correct_{step_id}_{i}", False) or 
        st.session_state.get(f"text_correct_{step_id}_{i}", False)
        for i in range(question_count)
    )

    if all_questions_correct:
        st.success("You have answered all questions correctly! You can proceed to the next path.")
else:
    st.write("You have completed the path!")

# Always display the Next button
if st.button("Next"):
    next_step()
    st.experimental_rerun()

# Custom CSS to position the footer container
st.markdown("""
    <style>
    .css-18e3th9 {
        float: bottom;
    }
    </style>
""", unsafe_allow_html=True)

# Create footer container for the microphone
footer_container = st.container()
footer_container.float("bottom: 0rem;")
