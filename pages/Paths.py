import streamlit as st
import json
import os
import tempfile
import string
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from utils import speech_to_text, text_to_speech, get_answer
from fuzzywuzzy import fuzz
import difflib

# Load environment variables
load_dotenv()

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

# Function to check if a phrase is contained within the response
def contains_phrase(response, phrase):
    return phrase.lower() in response.lower()

# Function to highlight errors in the response
def highlight_errors(user_response, correct_answer):
    matcher = difflib.SequenceMatcher(None, user_response, correct_answer)
    highlighted_user_response = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            highlighted_user_response.append(user_response[i1:i2])
        elif tag == 'replace' or tag == 'delete':
            highlighted_user_response.append(f"<span style='color: red; text-decoration: underline;'>{user_response[i1:i2]}</span>")
        elif tag == 'insert':
            highlighted_user_response.append(f"<span style='color: red; text-decoration: underline;'>{correct_answer[j1:j2]}</span>")
    return ''.join(highlighted_user_response)

# Function to handle audio response
def handle_audio_response(prompt, correct_answer, key, check_partial=False):
    audio_data = audio_recorder(f"Record your response:", key=key, pause_threshold=2.5, icon_size="2x")
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_file.write(audio_data)
            audio_file_path = audio_file.name

        transcription = speech_to_text(audio_file_path)
        normalized_transcription = normalize_text(transcription)
        normalized_correct_answer = normalize_text(correct_answer)

        similarity_score = fuzz.ratio(normalized_transcription, normalized_correct_answer)
        percentage_correct = similarity_score

        if check_partial:
            if contains_phrase(normalized_transcription, normalized_correct_answer):
                st.write(f"You Said: {transcription}")
                st.success("Correct answer!")
                st.session_state[f"audio_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(transcription, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"audio_correct_{key}"] = False
        else:
            if fuzz.ratio(normalized_transcription, normalized_correct_answer) >= 90:
                st.write(f"You Said: {transcription}")
                st.success("Correct answer!")
                st.session_state[f"audio_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(transcription, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"audio_correct_{key}"] = False

# Function to handle text response
def handle_text_response(prompt, correct_answer, key, check_partial=False):
    user_response = st.text_input("Your answer", key=key)
    if st.button("Submit", key=f"submit_{key}"):
        normalized_user_response = normalize_text(user_response)
        normalized_correct_answer = normalize_text(correct_answer)

        similarity_score = fuzz.ratio(normalized_user_response, normalized_correct_answer)
        percentage_correct = similarity_score

        if check_partial:
            if contains_phrase(normalized_user_response, normalized_correct_answer):
                st.write(f"You Said: {user_response}")
                st.success("Correct answer!")
                st.session_state[f"text_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(user_response, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"text_correct_{key}"] = False
        else:
            if fuzz.ratio(normalized_user_response, normalized_correct_answer) >= 90:
                st.write(f"You Said: {user_response}")
                st.success("Correct answer!")
                st.session_state[f"text_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(user_response, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"text_correct_{key}"] = False

# Bot Talk Template
def bot_talk_template(data, question_number):
    st.write(f"Question {question_number}: {data['phrases']}")

    if "bot_convo_state" not in st.session_state:
        st.session_state.bot_convo_state = {
            "conversation_history": [{"role": "assistant", "content": data['phrases']}],
            "key_counter": 0,
            "status": "waiting for you to speak (click the button)"
        }

    # Display conversation history
    for message in st.session_state.bot_convo_state['conversation_history']:
        if message['role'] == 'user':
            st.write(f"You: {message['content']}")
        else:
            st.write(f"Bot: {message['content']}")

    # Record audio response
    audio_data = audio_recorder(f"Record your response:", key=f"bot_convo_audio_{data['id']}_{question_number}_{st.session_state.bot_convo_state['key_counter']}", pause_threshold=2.5, icon_size="2x")

    # Process the recorded audio response
    if audio_data:
        st.session_state.bot_convo_state['status'] = "listening..."
        st.session_state.bot_convo_state['key_counter'] += 1
        process_bot_audio_response(audio_data, data, question_number)

def process_bot_audio_response(audio_data, data, question_number):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
        audio_file.write(audio_data)
        audio_file_path = audio_file.name

    transcription = speech_to_text(audio_file_path)
    st.session_state.bot_convo_state['conversation_history'].append({"role": "user", "content": transcription})
    st.session_state.bot_convo_state['status'] = "analyzing..."
    
    system_prompt = "You are an English coach. Continue the conversation based on the user's input."
    assistant_response = get_answer(st.session_state.bot_convo_state['conversation_history'], system_prompt)
    st.session_state.bot_convo_state['conversation_history'].append({"role": "assistant", "content": assistant_response})
    text_to_speech(assistant_response)

    st.session_state.bot_convo_state['status'] = "waiting for you to speak (click the button)"
    st.experimental_rerun()

# Template functions
def video_template(data, question_number):
    st.write(f"Question {question_number}: Video")
    st.video(data['content'])
    for i, question in enumerate(data['questions']):
        st.write(question['question'])
        handle_audio_response(question['question'], question['correct_answer'], key=f"video_audio_{data['id']}_{i}")
        handle_text_response(question['question'], question['correct_answer'], key=f"video_text_{data['id']}_{i}")

def speak_out_loud_template(data, question_number):
    st.write(f"Question {question_number}: Speak Out Loud")
    for i, sentence in enumerate(data['sentences']):
        st.write(sentence)
        handle_audio_response(sentence, sentence, key=f"speakOutLoud_audio_{data['id']}_{i}")
        handle_text_response(sentence, sentence, key=f"speakOutLoud_text_{data['id']}_{i}")

def voice_quiz_template(data, question_number):
    st.write(f"Question {question_number}: Voice Quiz")
    for i, question in enumerate(data['questions']):
        st.write(question['question'])
        handle_audio_response(question['question'], question['correct_answer'], key=f"voiceQuiz_audio_{data['id']}_{i}")

def text_quiz_template(data, question_number):
    st.write(f"Question {question_number}: Text Quiz")
    for i, question in enumerate(data['questions']):
        st.write(question['question'])
        handle_text_response(question['question'], question['correct_answer'], key=f"textQuiz_text_{data['id']}_{i}")

# Initialize session state
def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

initialize_session_state()

def next_step():
    st.session_state.current_step += 1

def render_step(step, question_number):
    step_type = step['type']
    if step_type == 'video':
        video_template(step, question_number)
    elif step_type == 'botTalk':
        bot_talk_template(step, question_number)
    elif step_type == 'speakOutLoud':
        speak_out_loud_template(step, question_number)
    elif step_type == 'textQuiz':
        text_quiz_template(step, question_number)
    elif step_type == 'voiceQuiz':
        voice_quiz_template(step, question_number)

st.title("Interactive Learning Path")

steps = question_data['questions']
current_step_index = st.session_state.current_step

if current_step_index < len(steps):
    step = steps[current_step_index]
    question_number = current_step_index + 1
    render_step(step, question_number)

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
