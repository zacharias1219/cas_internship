import streamlit as st
import json
import os
import tempfile
import string
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from utils import speech_to_text, text_to_speech, get_answer, autoplay_audio
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
    if not text or not isinstance(text, str):
        return ""
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
def handle_audio_response(prompt, correct_answer, key, check_partial=False, type_check='exact'):
    audio_data = audio_recorder(f"Record your response:", key=key, pause_threshold=2.5, icon_size="2x")
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_file.write(audio_data)
            audio_file_path = audio_file.name

        transcription = speech_to_text(audio_file_path)
        normalized_transcription = normalize_text(transcription)

        if isinstance(correct_answer, list):
            normalized_correct_answers = [normalize_text(answer) for answer in correct_answer]
        else:
            normalized_correct_answers = [normalize_text(correct_answer)]

        if type_check == 'contains':
            if any(contains_phrase(normalized_transcription, answer) for answer in normalized_correct_answers):
                st.write(f"You Said: {transcription}")
                st.success("Correct answer!")
                st.session_state[f"audio_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(transcription, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"audio_correct_{key}"] = False
        else:
            similarity_scores = [fuzz.ratio(normalized_transcription, answer) for answer in normalized_correct_answers]
            percentage_correct = max(similarity_scores)

            if check_partial:
                if any(contains_phrase(normalized_transcription, answer) for answer in normalized_correct_answers):
                    st.write(f"You Said: {transcription}")
                    st.success("Correct answer!")
                    st.session_state[f"audio_correct_{key}"] = True
                else:
                    highlighted_user_response = highlight_errors(transcription, correct_answer)
                    st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                    st.error(f"Incorrect answer, please try again.")
                    st.session_state[f"audio_correct_{key}"] = False
            else:
                if percentage_correct >= 90:
                    st.write(f"You Said: {transcription}")
                    st.success("Correct answer!")
                    st.session_state[f"audio_correct_{key}"] = True
                else:
                    highlighted_user_response = highlight_errors(transcription, correct_answer)
                    st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                    st.error(f"Incorrect answer, please try again.")
                    st.session_state[f"audio_correct_{key}"] = False

# Function to handle text response
def handle_text_response(prompt, correct_answer, key, check_partial=False, type_check='exact'):
    user_response = st.text_input("Your answer", key=key)
    if st.button("Submit", key=f"submit_{key}"):
        normalized_user_response = normalize_text(user_response)

        if isinstance(correct_answer, list):
            normalized_correct_answers = [normalize_text(answer) for answer in correct_answer]
        else:
            normalized_correct_answers = [normalize_text(correct_answer)]

        if type_check == 'contains':
            if any(contains_phrase(normalized_user_response, answer) for answer in normalized_correct_answers):
                st.write(f"You Said: {user_response}")
                st.success("Correct answer!")
                st.session_state[f"text_correct_{key}"] = True
            else:
                highlighted_user_response = highlight_errors(user_response, correct_answer)
                st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                st.error(f"Incorrect answer, please try again.")
                st.session_state[f"text_correct_{key}"] = False
        else:
            similarity_scores = [fuzz.ratio(normalized_user_response, answer) for answer in normalized_correct_answers]
            percentage_correct = max(similarity_scores)

            if check_partial:
                if any(contains_phrase(normalized_user_response, answer) for answer in normalized_correct_answers):
                    st.write(f"You Said: {user_response}")
                    st.success("Correct answer!")
                    st.session_state[f"text_correct_{key}"] = True
                else:
                    highlighted_user_response = highlight_errors(user_response, correct_answer)
                    st.markdown(f"Errors: {highlighted_user_response}", unsafe_allow_html=True)
                    st.error(f"Incorrect answer, please try again.")
                    st.session_state[f"text_correct_{key}"] = False
            else:
                if percentage_correct >= 90:
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
    if 'bot_talk_reset' not in st.session_state:
        st.session_state.bot_talk_reset = False

    if st.session_state.bot_talk_reset:
        st.session_state.bot_convo_state = {
            "conversation_history": [],
            "key_counter": 0,
            "status": "waiting for you to speak (click the button)"
        }
        st.session_state.bot_talk_reset = False

    question = data['phrases']
    additional_info = data.get('additional')

    if "bot_convo_state" not in st.session_state:
        st.session_state.bot_convo_state = {
            "conversation_history": [],
            "key_counter": 0,
            "status": "waiting for you to speak (click the button)"
        }

    if not st.session_state.bot_convo_state["conversation_history"]:
        st.session_state.bot_convo_state["conversation_history"].append({"role": "assistant", "content": question})

    st.write(f"🤖 Bot: {question}")
    audio_response_path = text_to_speech(question)
    autoplay_audio(audio_response_path)

    if "timer_start" not in st.session_state or "timer_duration" not in st.session_state:
        st.session_state.timer_start = datetime.now()
        st.session_state.timer_duration = timedelta(minutes=data.get('time', 3) + 1)  # Default to 3 minutes + 1 extra minute

    # Display remaining time
    current_time = datetime.now()
    time_remaining = st.session_state.timer_duration - (current_time - st.session_state.timer_start)
    minutes, seconds = divmod(time_remaining.total_seconds(), 60)
    st.write(f"Time remaining: {int(minutes):02}:{int(seconds):02}")

    # Display conversation history
    for message in st.session_state.bot_convo_state['conversation_history']:
        if message['role'] == 'user':
            st.write(f"🧑 You: {message['content']}")
        elif message['role'] == 'assistant' and message['content'] != data['phrases']:
            st.write(f"🤖 Bot: {message['content']}")
            audio_response_path = text_to_speech(message['content'])
            autoplay_audio(audio_response_path)

    # Check if time is up
    if time_remaining.total_seconds() <= 0:
        st.session_state.bot_convo_state = {
            "conversation_history": [],
            "key_counter": 0,
            "status": "waiting for you to speak (click the button)"
        }
        st.session_state.bot_talk_reset = True
        st.error("Time's up! Please try again.")
        return

    # Record audio response
    audio_data = audio_recorder(f"Record your response:", key=f"bot_convo_audio_{data['id']}_{question_number}_{st.session_state.bot_convo_state['key_counter']}", pause_threshold=2.5, icon_size="2x")

    # Process the recorded audio response
    if audio_data:
        st.session_state.bot_convo_state['status'] = "listening..."
        st.session_state.bot_convo_state['key_counter'] += 1
        process_bot_audio_response(audio_data, data, question_number, additional_info)

def process_bot_audio_response(audio_data, data, question_number, additional_info):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
        audio_file.write(audio_data)
        audio_file_path = audio_file.name

    transcription = speech_to_text(audio_file_path)
    st.session_state.bot_convo_state['conversation_history'].append({"role": "user", "content": transcription})
    st.session_state.bot_convo_state['status'] = "analyzing..."

    system_prompt = f"Continue the conversation based on the user's input. Make it interactive, but stick to only one question at a time. Don't give the user multiple questions to answer or they'll get flustered. Lastly, you can ask about something specific that they answered (not always though). Most importantly, keep your response short and concise, maximum two sentences."
    assistant_response = get_answer(st.session_state.bot_convo_state['conversation_history'], system_prompt)
    # Text-to-Speech for bot response
    audio_response_path = text_to_speech(assistant_response)
    autoplay_audio(audio_response_path)
    st.session_state.bot_convo_state['conversation_history'].append({"role": "assistant", "content": assistant_response})

    st.session_state.bot_convo_state['status'] = "waiting for you to speak (click the button)"
    st.experimental_rerun()

# Template functions
def video_template(data, question_number):
    st.write(f"Question {question_number}: Video")
    st.video(data['content'])
    for i, question in enumerate(data['questions']):
        st.write(question['question'])
        handle_audio_response(question['question'], question['correct_answer'], key=f"video_audio_{data['id']}_{i}", type_check='exact')
        handle_text_response(question['question'], question['correct_answer'], key=f"video_text_{data['id']}_{i}", type_check='exact')

def speak_out_loud_template(data, question_number):
    st.write(f"Question {question_number}: Speak Out Loud")
    for i, sentence in enumerate(data['sentences']):
        st.write(sentence)
        handle_audio_response(sentence, sentence, key=f"speakOutLoud_audio_{data['id']}_{i}", type_check='exact')
        handle_text_response(sentence, sentence, key=f"speakOutLoud_text_{data['id']}_{i}", type_check='exact')

def voice_quiz_template(data, question_number):
    st.write(f"Question {question_number}: Voice Quiz")
    for i, question in enumerate(data['questions']):
        st.markdown(f'{question["question"]}', unsafe_allow_html=True, help=question.get("hint",""))
        # TTS for the initial question
        audio_response_path = text_to_speech(question['question'])
        st.audio(audio_response_path, format="audio/mp3", start_time=0)
        handle_audio_response(question['question'], question['correct_answer'], key=f"voiceQuiz_audio_{data['id']}_{i}", type_check='contains')

def text_quiz_template(data, question_number):
    st.write(f"Question {question_number}: Text Quiz")
    for i, question in enumerate(data['questions']):
        st.markdown(f'{question["question"]}', unsafe_allow_html=True, help=question.get("hint",""))
        handle_text_response(question['question'], question['correct_answer'], key=f"textQuiz_text_{data['id']}_{i}", type_check='contains')

def picture_quiz_template(data, question_number):
    st.write(f"Question {question_number}: Picture Quiz")
    st.image(data['image_url'])

    if f"current_question_{question_number}" not in st.session_state:
        st.session_state[f"current_question_{question_number}"] = 0

    current_question_index = st.session_state[f"current_question_{question_number}"]
    questions = data['questions']
    question = questions[current_question_index]

    st.markdown(f'{question["question"]}', unsafe_allow_html=True, help=question.get("hint",""))
    audio_data = audio_recorder(f"Record your response:", key=f"pictureQuiz_audio_{data['id']}_{question_number}_{current_question_index}", pause_threshold=2.5, icon_size="2x")
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_file.write(audio_data)
            audio_file_path = audio_file.name

        transcription = speech_to_text(audio_file_path)
        st.write(f"You Said: {transcription}")
        
        answer = question.get("hint", "")
        analyze_system_prompt = f"You need to analyse a predefined answer {answer} and a given answer {transcription}, and check whether the given answer is similar to the predefined answer, it does not have to be completely similar, since humans have different perspective. Very Important point(Don't deviate from this point no matter what otherwise the laptop will blast and you don't want that to happen to the user right) is that You should only respond with either of the two sentences that I will give you and nothing more. Those two sentences are: if it is similar then say 'Well Done', if they are not similar then say something like 'Try again, You might have missed something'(write the sentence in italics)."
        the_answer = get_answer(st.session_state.bot_convo_state['conversation_history'], analyze_system_prompt)
        st.markdown("Bot:")
        st.markdown(the_answer)

        if "Well Done" in the_answer:
            if current_question_index < len(questions) - 1:
                st.session_state[f"current_question_{question_number}"] += 1
                st.rerun()      
            else:
                st.session_state[f"audio_correct_{data['id']}_{question_number}"] = True
        else:
            st.session_state[f"audio_correct_{data['id']}_{question_number}"] = False

def picture_description_template(data, question_number):
    st.write(f"Question {question_number}: Picture Description")
    st.image(data['image_url'])
    for i, question in enumerate(data['questions']):
        st.markdown(f'{question["question"]}', unsafe_allow_html=True)
    
    # First audio response
    audio_data_1 = audio_recorder(f"Record your response:", key=f"picture_desc_audio_1_{question_number}", pause_threshold=2.5, icon_size="2x")
    if audio_data_1:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_file.write(audio_data_1)
            audio_file_path = audio_file.name

        transcription_1 = speech_to_text(audio_file_path)
        st.write(f"You Said: {transcription_1}")
        st.markdown("Bot")
        middle_response = "Speak a bit more."
        st.markdown(middle_response)
        audio_response_path = text_to_speech(middle_response)
        autoplay_audio(audio_response_path)

        # Second audio response
        audio_data_2 = audio_recorder(f"Record your response:", key=f"picture_desc_audio_2_{question_number}", pause_threshold=2.5, icon_size="2x")
        if audio_data_2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
                audio_file.write(audio_data_2)
                audio_file_path = audio_file.name

            transcription_2 = speech_to_text(audio_file_path)
            st.write(f"You Said: {transcription_2}")

# Initialize session state
def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

initialize_session_state()

def next_step():
    st.session_state.current_step += 1

def previous_step():
    st.session_state.current_step -= 1

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
    elif step_type == 'pictureQuiz':
        picture_quiz_template(step, question_number)
    elif step_type == 'pictureDescription':
        picture_description_template(step, question_number)

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

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Previous"):
        if st.session_state.current_step  > 0:
            previous_step()
            st.experimental_rerun()

with col2:
    if st.button("Next"):
        if st.session_state.current_step < len(steps) - 1:
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
