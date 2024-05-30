import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

st.set_page_config(
    page_title="Interview Bot",
    layout="wide",
    page_icon="💬",
    initial_sidebar_state="collapsed",
)

# Float feature initialization
float_init()

# Define interview scenarios and their respective system prompts
scenarios = {
    "Java Interview": "You are an experienced interviewer conducting a comprehensive Java programming interview session with the user. Your role is to ask a variety of Java-specific interview questions, covering topics such as OOP concepts, Java syntax, Java libraries, and problem-solving using Java. After each response, you provide insightful feedback, highlighting strengths and areas for improvement. You will assess their knowledge and skills in Java programming.",
    "Excel Interview": "You are an experienced interviewer conducting a comprehensive Excel skills interview session with the user. Your role is to ask a variety of Excel-specific interview questions, covering topics such as Excel formulas, data analysis, pivot tables, and VBA macros. After each response, you provide insightful feedback, highlighting strengths and areas for improvement. You will assess their knowledge and skills in using Excel effectively."
}

content = {
    "Java Interview": "Welcome to the Java interview. Let's start with your introduction.",
    "Excel Interview": "Welcome to the Excel interview. Let's start with your introduction."
}

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": content["Java Interview"]}]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Java Interview"
    if "previous_scenario" not in st.session_state:
        st.session_state.previous_scenario = "Java Interview"
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_level" not in st.session_state:
        st.session_state.current_level = 1

initialize_session_state()

st.title("Interview Bot 🤖")

# Function to lock stages
def lock_stages(current_level):
    locked_stages = {"Java Interview": 1, "Excel Interview": 2}  # Define the level required for each stage
    return {stage: level <= current_level for stage, level in locked_stages.items()}

locked_stages = lock_stages(st.session_state.current_level)

# Use columns to place the dropdown, audio recorder, and end session button side by side
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Scenario selection
    available_scenarios = [scenario for scenario, unlocked in locked_stages.items() if unlocked]
    selected_scenario = st.selectbox(
        "Choose an interview",
        available_scenarios,
        index=0
    )

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

# Update the session state if the scenario changes
if selected_scenario != st.session_state.selected_scenario:
    st.session_state.selected_scenario = selected_scenario
    st.session_state.messages = [{"role": "assistant", "content": content[selected_scenario]}]

system_prompt = scenarios[selected_scenario]

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
            st.session_state.answers.append(transcript)  # Store the user's answer
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

# Evaluation button
if st.button("Evaluate Answers"):
    if len(st.session_state.answers) >= 10:  # Ensure there are enough answers to evaluate
        # Here you would normally have a more sophisticated evaluation
        score = sum(1 for answer in st.session_state.answers if "correct" in answer.lower())  # Simple placeholder
        if score / len(st.session_state.answers) >= 0.8:
            st.session_state.current_level += 1
            st.write(f"Congratulations! You've passed to level {st.session_state.current_level}.")
            st.experimental_rerun()  # Reload to update locked stages
        else:
            st.write("You did not pass. Please try again.")
    else:
        st.write("Not enough answers to evaluate.")

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
