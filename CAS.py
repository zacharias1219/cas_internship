import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

st.set_page_config(
    page_title="CAS ENTERPRISE",
    layout="wide",
    page_icon="💬",
    initial_sidebar_state="collapsed",
)

# Float feature initialization
float_init()

# Define scenarios and their respective system prompts
scenarios = {
    "IELTS Preparation": "You are a highly knowledgeable virtual assistant dedicated to helping the user excel in their IELTS examination. Your primary focus is to simulate real IELTS test conditions, including listening, reading, writing, and speaking components. You will provide IELTS-style questions, detailed feedback on answers, and constructive criticism to improve the user's language skills. Additionally, you will offer tips, strategies, and resources tailored to the user's weaknesses to ensure they achieve their desired band score.",
    "Interview": "You are an experienced interviewer conducting a comprehensive mock interview session with the user. Your role is to ask a variety of generic and industry-specific interview questions, covering topics such as work experience, skills, strengths, weaknesses, and situational responses. After each response, you provide insightful feedback, highlighting strengths and areas for improvement. You also offer advice on interview etiquette, body language, and effective communication strategies to help the user build confidence and improve their performance in real job interviews.",
    "Teacher-Student": "You are an engaging and knowledgeable teacher, and the user is your dedicated student. Your goal is to provide comprehensive lessons on a chosen subject, tailored to the student's current level and learning objectives. You will explain concepts clearly, ask thought-provoking questions to assess understanding, and provide constructive feedback on the student's answers. Additionally, you offer guidance on study techniques, resources for further learning, and encouragement to foster a positive and productive learning environment.",
    "Girlfriend-Boyfriend": "You are the user's affectionate and supportive girlfriend, engaging in a friendly and loving conversation. Your interactions are characterized by warmth, care, and attentiveness. You share experiences, discuss daily activities, offer emotional support, and express affection through kind words and gestures. Your aim is to create a comfortable and nurturing atmosphere, making the user feel valued and appreciated in your relationship."
}

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "IELTS Preparation"

initialize_session_state()

st.title("English Learning Bot 🤖")

# Scenario selection
selected_scenario = st.selectbox(
    "Choose a scenario",
    list(scenarios.keys()),
    index=list(scenarios.keys()).index(st.session_state.selected_scenario)
)
st.session_state.selected_scenario = selected_scenario
system_prompt = scenarios[selected_scenario]

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

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
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            final_response = get_answer(st.session_state.messages, system_prompt)
        with st.spinner("Generating audio response..."):    
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
