import streamlit as st
import json
import os
from utils import speech_to_text, normalize_text
from audio_recorder_streamlit import audio_recorder

# Load questions data
with open('questions.json', 'r', encoding='utf-8') as qf:
    question_data = json.load(qf)

# Initialize session state
def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'current_path' not in st.session_state:
        st.session_state.current_path = question_data['paths'][0]
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0

initialize_session_state()

# Function to handle audio response
def handle_audio_response(sentence):
    audio_data = audio_recorder("Record your response", key=f"audio_{sentence}")
    if audio_data is not None:
        with open("temp_audio.wav", "wb") as file:
            file.write(audio_data)
        transcription = speech_to_text("temp_audio.wav")
        st.write(f"Transcription: {transcription}")
        normalized_transcription = normalize_text(transcription)
        normalized_correct_answer = normalize_text(sentence)
        st.write(f"Normalized Transcription: {normalized_transcription}")
        st.write(f"Normalized Correct Answer: {normalized_correct_answer}")
        if normalized_transcription == normalized_correct_answer:
            st.success("Correct answer!")
            return True
        else:
            st.error("Incorrect answer, please try again.")
            return False
    return False

# Function to handle text response
def handle_text_response(question, correct_answer):
    user_answer = st.text_input("Your answer", key=f"text_{question}")
    if user_answer:
        normalized_user_answer = normalize_text(user_answer)
        normalized_correct_answer = normalize_text(correct_answer)
        st.write(f"Normalized User Answer: {normalized_user_answer}")
        st.write(f"Normalized Correct Answer: {normalized_correct_answer}")
        if normalized_user_answer == normalized_correct_answer:
            st.success("Correct answer!")
            return True
        else:
            st.error("Incorrect answer, please try again.")
            return False
    return False

# Function to render each step based on its type
def render_step(step):
    step_type = step['type']
    step_data = step['data']

    if step_type == 'speakOutLoud':
        st.write("Speak Out Loud")
        for sentence in step_data['sentences']:
            st.write(f"Please say '{sentence}'")
            if handle_audio_response(sentence):
                st.session_state.correct_answers += 1

    elif step_type == 'botTalk':
        st.write("Bot Talk")
        for phrase in step_data['phrases']:
            st.write(phrase)
            if handle_text_response(phrase, phrase):
                st.session_state.correct_answers += 1

    elif step_type == 'pronunciations':
        st.write("Pronunciations")
        for word in step_data['words']:
            st.write(word)
            if handle_text_response(word, word):
                st.session_state.correct_answers += 1

# Function to proceed to the next step if all questions are correct
def next_step():
    st.session_state.current_step += 1
    st.session_state.correct_answers = 0

# Main application logic
st.title("Interactive Learning Path")

current_path = st.session_state.current_path
current_step_index = st.session_state.current_step
steps = current_path['steps']
total_questions = sum(len(step['data'].get('sentences', [])) + len(step['data'].get('phrases', [])) + len(step['data'].get('words', [])) for step in steps)

if current_step_index < len(steps):
    step = steps[current_step_index]
    render_step(step)
    st.write(f"Progress: {st.session_state.correct_answers}/{total_questions}")
    if st.session_state.correct_answers == total_questions:
        next_step()
else:
    st.write("You have completed the path!")
