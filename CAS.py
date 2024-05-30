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

# Define interview scenarios, levels, and their respective system prompts
scenarios = {
    "Java Interview": {
        "Beginner": "You are an experienced interviewer conducting a beginner level Java programming interview session with the user. Ask about basic OOP concepts, Java syntax, and simple problem-solving.",
        "Intermediate": "You are an experienced interviewer conducting an intermediate level Java programming interview session with the user. Ask about advanced OOP concepts, Java libraries, and moderate problem-solving.",
        "Hard": "You are an experienced interviewer conducting a hard level Java programming interview session with the user. Ask about complex problem-solving, design patterns, and performance optimization in Java."
    },
    "Excel Interview": {
        "Beginner": "You are an experienced interviewer conducting a beginner level Excel skills interview session with the user. Ask about basic Excel formulas, data entry, and simple data manipulation.",
        "Intermediate": "You are an experienced interviewer conducting an intermediate level Excel skills interview session with the user. Ask about advanced Excel formulas, data analysis, and pivot tables.",
        "Hard": "You are an experienced interviewer conducting a hard level Excel skills interview session with the user. Ask about VBA macros, complex data analysis, and automation in Excel."
    }
}

content = {
    "Java Interview": {
        "Beginner": "Welcome to the beginner level Java interview. Let's start with your introduction.",
        "Intermediate": "Welcome to the intermediate level Java interview. Let's start with your introduction.",
        "Hard": "Welcome to the hard level Java interview. Let's start with your introduction."
    },
    "Excel Interview": {
        "Beginner": "Welcome to the beginner level Excel interview. Let's start with your introduction.",
        "Intermediate": "Welcome to the intermediate level Excel interview. Let's start with your introduction.",
        "Hard": "Welcome to the hard level Excel interview. Let's start with your introduction."
    }
}

levels = ["Beginner", "Intermediate", "Hard"]

# Expected answers for each scenario and level
expected_answers = {
    "Java Interview": {
        "Beginner": ["OOP stands for Object-Oriented Programming", "Java is a high-level programming language", "A class in Java is a blueprint for objects"],
        "Intermediate": ["Inheritance allows a class to inherit methods and properties", "Polymorphism allows methods to do different things based on the object", "Encapsulation hides the internal state of an object"],
        "Hard": ["Design patterns provide solutions to common problems", "The Singleton pattern restricts instantiation of a class to one object", "Java's garbage collector manages memory"]
    },
    "Excel Interview": {
        "Beginner": ["SUM function adds all the numbers in a range of cells", "A cell reference refers to a cell or a range of cells on a worksheet", "A pivot table summarizes data"],
        "Intermediate": ["VLOOKUP searches for a value in the first column of a table range", "Conditional formatting changes the appearance of cells", "The IF function performs a logical test and returns one value for a TRUE result and another for a FALSE result"],
        "Hard": ["VBA stands for Visual Basic for Applications", "Macros automate repetitive tasks", "Power Query is used for data connection and transformation"]
    }
}

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": content["Java Interview"]["Beginner"]}]
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Java Interview"
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = "Beginner"
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "level_progress" not in st.session_state:
        st.session_state.level_progress = {"Java Interview": "Beginner", "Excel Interview": "Beginner"}
    if "incorrect_attempts" not in st.session_state:
        st.session_state.incorrect_attempts = 0

initialize_session_state()

st.title("Interview Bot 🤖")

# Function to determine if the next level is unlocked
def unlock_next_level(current_level):
    if current_level == "Beginner":
        return "Intermediate"
    elif current_level == "Intermediate":
        return "Hard"
    else:
        return None

# Use columns to place the dropdown, audio recorder, and end session button side by side
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Scenario selection
    selected_scenario = st.selectbox(
        "Choose an interview",
        list(scenarios.keys()),
        index=list(scenarios.keys()).index(st.session_state.selected_scenario)
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

# Update the session state if the scenario changes
if selected_scenario != st.session_state.selected_scenario:
    st.session_state.selected_scenario = selected_scenario
    st.session_state.selected_level = "Beginner"
    st.session_state.messages = [{"role": "assistant", "content": content[selected_scenario]["Beginner"]}]
    st.session_state.answers = []
    st.session_state.incorrect_attempts = 0

system_prompt = scenarios[selected_scenario][st.session_state.level_progress[selected_scenario]]

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
def evaluate_answers(user_answers, expected_answers):
    score = 0
    seen_answers = set()

    for user_answer, expected_answer in zip(user_answers, expected_answers):
        # Remove leading and trailing whitespaces and convert to lowercase
        user_answer_clean = user_answer.strip().lower()

        # Check for cases to exclude
        if not user_answer_clean:  # Empty or whitespace only
            continue
        if user_answer_clean in seen_answers:  # Repeated answer
            continue
        if "explain" in user_answer_clean or "again" in user_answer_clean:  # Asking to explain again
            continue
        if not any(keyword in user_answer_clean for keyword in expected_answer.lower().split()):  # Non-relevant answer
            continue

        # Simple keyword matching; could be improved with more sophisticated NLP techniques
        if all(keyword.lower() in user_answer_clean for keyword in expected_answer.split()):
            score += 1

        seen_answers.add(user_answer_clean)

    return score

def handle_answer(user_answer, expected_answer):
    # Remove leading and trailing whitespaces and convert to lowercase
    user_answer_clean = user_answer.strip().lower()

    # Check for non-answer cases
    if not user_answer_clean or "explain" in user_answer_clean or "again" in user_answer_clean:
        return "not an answer"
    
    # Simple keyword matching to check if the answer is correct
    if all(keyword.lower() in user_answer_clean for keyword in expected_answer.split()):
        st.session_state.incorrect_attempts = 0  # Reset incorrect attempts on correct answer
        return "correct"

    st.session_state.incorrect_attempts += 1
    if st.session_state.incorrect_attempts == 3:
        return "explain and move on"
    elif st.session_state.incorrect_attempts == 2:
        return "explain briefly"
    else:
        return "incorrect"

if st.button("Evaluate Answers"):
    if len(st.session_state.answers) >= 10:  # Ensure there are enough answers to evaluate
        scenario_answers = expected_answers[selected_scenario][st.session_state.level_progress[selected_scenario]]
        user_answers = st.session_state.answers[:10]
        
        for user_answer, expected_answer in zip(user_answers, scenario_answers):
            result = handle_answer(user_answer, expected_answer)
            if result == "correct":
                st.write("Correct! Moving to the next question.")
                st.session_state.answers.remove(user_answer)
                break
            elif result == "incorrect":
                st.write("That's not quite right. Let's try again.")
                break
            elif result == "explain briefly":
                st.write("That's not quite right. Here's a brief explanation: " + expected_answer)
                break
            elif result == "explain and move on":
                st.write("That's not quite right. Here's a detailed explanation: " + expected_answer)
                st.session_state.incorrect_attempts = 0  # Reset incorrect attempts
                break
            elif result == "not an answer":
                st.write("Please provide a relevant answer.")
                break
        
        if st.session_state.incorrect_attempts == 0 and result == "correct":
            # Check if all answers were correct and move to next level
            score = evaluate_answers(user_answers, scenario_answers)
            if score / len(user_answers) >= 0.05:
                next_level = unlock_next_level(st.session_state.level_progress[selected_scenario])
                if next_level:
                    st.session_state.level_progress[selected_scenario] = next_level
                    st.session_state.selected_level = next_level
                    st.session_state.messages = [{"role": "assistant", "content": content[selected_scenario][next_level]}]
                    st.session_state.answers = []
                    st.write(f"Congratulations! You've passed to the {next_level} level.")
                    st.experimental_rerun()  # Reload to update available levels
                else:
                    st.write("You have completed all levels. Congratulations!")
            else:
                st.write("You did not pass. Please try again.")
    else:
        st.write("Not enough answers to evaluate.")

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")
