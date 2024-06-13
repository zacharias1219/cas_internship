import streamlit as st
import json
import random
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import openai
import tempfile

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Load the question and video data from JSON files
with open('questions.json', encoding='utf-8') as qf:
    question_data = json.load(qf)

with open('videos.json', encoding='utf-8') as vf:
    video_data = json.load(vf)

# Function to capture audio
def capture_audio():
    audio_data = st.audio("Record your response", format="audio/wav")
    return audio_data

# Function to transcribe audio using OpenAI's Whisper
def transcribe_audio(audio_data):
    openai.api_key = openai_api_key
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_file.write(audio_data.getbuffer())
    audio_file.close()
    
    response = openai.Audio.transcribe(file=openai.AudioFile(audio_file.name))
    return response['text']

# Function to handle audio response
def handle_audio_response(correct_answer):
    audio_data = capture_audio()
    if audio_data:
        transcription = transcribe_audio(audio_data)
        if transcription.lower().strip() == correct_answer.lower().strip():
            st.success("Correct answer!")
            next_step()
        else:
            st.error("Incorrect answer, please try again.")

# Function to validate text response
def validate_text_response(user_answer, correct_answer):
    if user_answer.lower().strip() == correct_answer.lower().strip():
        st.success("Correct answer!")
        next_step()
    else:
        st.error("Incorrect answer, please try again.")

# Function to validate audio response
def validate_audio_response(correct_answer):
    audio_data = capture_audio()
    if audio_data:
        transcription = transcribe_audio(audio_data)
        if transcription.lower().strip() == correct_answer.lower().strip():
            st.success("Correct answer!")
            next_step()
        else:
            st.error("Incorrect answer, please try again.")

# Template functions
def quiz_template(data):
    st.write("Quiz")
    for question in data['questions']:
        st.write(question['content'])
        user_answer = st.text_input("Your answer", key=question['id'])
        if st.button("Submit", key=f"submit_{question['id']}"):
            validate_text_response(user_answer, question['correct_answer'])
        if st.button("Record", key=f"record_{question['id']}"):
            validate_audio_response(question['correct_answer'])

def video_template(data):
    st.write("Video")
    st.video(data['content'])
    for question in data['questions']:
        st.write(question['question'])
        user_answer = st.text_input("Your answer", key=question['id'])
        if st.button("Submit", key=f"submit_{question['id']}"):
            validate_text_response(user_answer, question['correct_answer'])
        if st.button("Record", key=f"record_{question['id']}"):
            validate_audio_response(question['correct_answer'])

def bot_talk_template(data):
    st.write("Bot Talk")
    for phrase in data['phrases']:
        st.write(phrase)
        user_answer = st.text_input("Your response", key=phrase)
        if st.button("Submit", key=f"submit_{phrase}"):
            validate_text_response(user_answer, phrase)
        if st.button("Record", key=f"record_{phrase}"):
            validate_audio_response(phrase)

def pronunciations_template(data):
    st.write("Pronunciations")
    for word in data['words']:
        st.write(word)
        user_answer = st.text_input("Your pronunciation", key=word)
        if st.button("Submit", key=f"submit_{word}"):
            validate_text_response(user_answer, word)
        if st.button("Record", key=f"record_{word}"):
            validate_audio_response(word)

def speak_out_loud_template(data):
    st.write("Speak Out Loud")
    for sentence in data['sentences']:
        st.write(sentence)
        user_answer = st.text_input("Your speech", key=sentence)
        if st.button("Submit", key=f"submit_{sentence}"):
            validate_text_response(user_answer, sentence)
        if st.button("Record", key=f"record_{sentence}"):
            validate_audio_response(sentence)

# Initialize session state
def initialize_session_state():
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    if 'current_path' not in st.session_state:
        st.session_state.current_path = get_new_path()
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

initialize_session_state()

def select_random_path():
    paths = ['quiz', 'video', 'botTalk', 'pronunciations', 'speakOutLoud']
    return random.choice(paths)

def select_random_questions(path_type, num_questions=5):
    filtered_questions = [q for q in question_data['questions'] if q['path'] == path_type]
    return random.sample(filtered_questions, min(len(filtered_questions), num_questions))

def get_new_path():
    path_type = select_random_path()
    questions = select_random_questions(path_type)
    return {
        'path_type': path_type,
        'questions': questions
    }

def next_step():
    st.session_state.current_step += 1
    if st.session_state.current_step >= len(st.session_state.current_path['questions']):
        st.session_state.current_section += 1
        st.session_state.current_step = 0
        if st.session_state.current_section < 12:
            st.session_state.current_path = get_new_path()

def render_step(step):
    step_type = step['type']
    step_data = step['data']
    if step_type == 'quiz':
        quiz_template(step_data)
    elif step_type == 'video':
        video_template(step_data)
    elif step_type == 'botTalk':
        bot_talk_template(step_data)
    elif step_type == 'pronunciations':
        pronunciations_template(step_data)
    elif step_type == 'speakOutLoud':
        speak_out_loud_template(step_data)

st.title("Interactive Learning Path")

current_path = st.session_state.current_path
current_step_index = st.session_state.current_step
steps = current_path['questions']

if current_step_index < len(steps):
    step = steps[current_step_index]
    render_step(step)
    st.button("Next", on_click=next_step)
else:
    st.write("You have completed the path!")
