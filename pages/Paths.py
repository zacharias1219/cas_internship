import streamlit as st
import json
import random
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import openai
import tempfile

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Load the question data from JSON files
def load_json(file_path):
    with open(file_path, encoding='utf-8') as file:
        return json.load(file)

question_data = load_json('questions.json')

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
def video_template(data):
    st.write("Video")
    st.video(data['content'])
    for question in data['questions']:
        st.write(question['question'])
        user_answer = st.text_input("Your answer", key=f"{data['id']}_{question['question']}")
        if st.button("Submit", key=f"submit_{data['id']}_{question['question']}"):
            validate_text_response(user_answer, question['correct_answer'])
        if st.button("Record", key=f"record_{data['id']}_{question['question']}"):
            validate_audio_response(question['correct_answer'])

def bot_talk_template(data):
    st.write("Bot Talk")
    for phrase in data['phrases']:
        st.write(phrase)
        user_answer = st.text_input("Your response", key=f"{data['id']}_{phrase}")
        if st.button("Submit", key=f"submit_{data['id']}_{phrase}"):
            validate_text_response(user_answer, phrase)
        if st.button("Record", key=f"record_{data['id']}_{phrase}"):
            validate_audio_response(phrase)

def pronunciations_template(data):
    st.write("Pronunciations")
    for word in data['words']:
        st.write(word)
        user_answer = st.text_input("Your pronunciation", key=f"{data['id']}_{word}")
        if st.button("Submit", key=f"submit_{data['id']}_{word}"):
            validate_text_response(user_answer, word)
        if st.button("Record", key=f"record_{data['id']}_{word}"):
            validate_audio_response(word)

def speak_out_loud_template(data):
    st.write("Speak Out Loud")
    for sentence in data['sentences']:
        st.write(sentence)
        user_answer = st.text_input("Your speech", key=f"{data['id']}_{sentence}")
        if st.button("Submit", key=f"submit_{data['id']}_{sentence}"):
            validate_text_response(user_answer, sentence)
        if st.button("Record", key=f"record_{data['id']}_{sentence}"):
            validate_audio_response(sentence)

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
        st.session_state.current_path = select_random_questions()
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

initialize_session_state()

def next_step():
    st.session_state.current_step += 1
    if st.session_state.current_step >= len(st.session_state.current_path):
        st.session_state.current_section += 1
        st.session_state.current_step = 0
        if st.session_state.current_section < 12:
            st.session_state.current_path = select_random_questions()

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
    st.button("Next", on_click=next_step)
else:
    st.write("You have completed the path!")
