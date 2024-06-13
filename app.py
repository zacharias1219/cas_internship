import streamlit as st
import json

# Load the path data from JSON file
with open('path_data.json') as f:
    path_data = json.load(f)

# Template functions
def quiz_template(data):
    st.write("Quiz")
    for question in data['questions']:
        st.write(question)
        st.text_input("Your answer", key=question)

def video_template(data):
    st.write("Video")
    st.video(data['url'])
    for question in data['questions']:
        st.write(question)
        st.text_input("Your answer", key=question)

def bot_talk_template(data):
    st.write("Bot Talk")
    for phrase in data['phrases']:
        st.write(phrase)
        st.text_input("Your response", key=phrase)

def pronunciations_template(data):
    st.write("Pronunciations")
    for word in data['words']:
        st.write(word)
        st.text_input("Your pronunciation", key=word)

def speak_out_loud_template(data):
    st.write("Speak Out Loud")
    for sentence in data['sentences']:
        st.write(sentence)
        st.text_input("Your speech", key=sentence)

# Initialize session state
def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'current_path' not in st.session_state:
        st.session_state.current_path = path_data['paths'][0]

initialize_session_state()

# Render the current step
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

def next_step():
    st.session_state.current_step += 1

st.title("Interactive Learning Path")

current_path = st.session_state.current_path
current_step_index = st.session_state.current_step
steps = current_path['steps']

if current_step_index < len(steps):
    step = steps[current_step_index]
    render_step(step)
    st.button("Next", on_click=next_step)
else:
    st.write("You have completed the path!")
