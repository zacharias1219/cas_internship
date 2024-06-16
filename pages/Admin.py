import streamlit as st
import json
import requests
import os

# Define the API URL
API_URL = "http://127.0.0.1:5000"

# Function to load question data from JSON file
def load_question_data():
    try:
        response = requests.get(f"{API_URL}/questions")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching questions: {e}")
        return {"questions": []}

# Load question data
question_data = load_question_data()

# Function to load existing submissions from the API
def get_submissions():
    try:
        response = requests.get(f"{API_URL}/submissions")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching submissions: {e}")
        return []

# Function to save a new submission to the API
def save_submission(submission):
    try:
        response = requests.post(f"{API_URL}/submissions", json=submission)
        response.raise_for_status()
        st.success("Submitted successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving submission: {e}")

# Function to delete a submission from the API
def delete_submission(index):
    try:
        response = requests.delete(f"{API_URL}/submissions/{index}")
        response.raise_for_status()
        st.success("Deleted successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting submission: {e}")

# Admin Page
st.title("Admin Page")

st.sidebar.title("Submit Content")
path_type = st.sidebar.selectbox("Path Type", ["video", "botTalk", "pronunciations", "speakOutLoud"])

if path_type == "video":
    video_url = st.sidebar.text_input("Video URL")
    question = st.sidebar.text_input("Question")
    correct_answer = st.sidebar.text_input("Correct Answer")
    if st.sidebar.button("Submit"):
        submission = {
            "type": "video",
            "content": video_url,
            "questions": [
                {
                    "question": question,
                    "correct_answer": correct_answer
                }
            ],
            "path": "video"
        }
        save_submission(submission)

elif path_type == "botTalk":
    phrases = st.sidebar.text_area("Phrases (comma separated)")
    if st.sidebar.button("Submit"):
        phrases_list = [phrase.strip() for phrase in phrases.split(',')]
        submission = {
            "type": "botTalk",
            "phrases": phrases_list,
            "path": "botTalk"
        }
        save_submission(submission)

elif path_type == "pronunciations":
    words = st.sidebar.text_area("Words (comma separated)")
    if st.sidebar.button("Submit"):
        words_list = [word.strip() for word in words.split(',')]
        submission = {
            "type": "pronunciations",
            "words": words_list,
            "path": "pronunciations"
        }
        save_submission(submission)

elif path_type == "speakOutLoud":
    sentences = st.sidebar.text_area("Sentences (comma separated)")
    if st.sidebar.button("Submit"):
        sentences_list = [sentence.strip() for sentence in sentences.split(',')]
        submission = {
            "type": "speakOutLoud",
            "sentences": sentences_list,
            "path": "speakOutLoud"
        }
        save_submission(submission)

st.write("Submissions")
submissions = get_submissions()
for i, submission in enumerate(submissions):
    st.write(submission)
    if st.button(f"Delete {i}", key=f"delete_{i}"):
        delete_submission(i)
        st.experimental_rerun()

# Function to verify and add submissions to the bank
def verify_submission(submission):
    if submission['type'] == 'video':
        return submission['content'] and submission['questions'][0]['question'] and submission['questions'][0]['correct_answer']
    elif submission['type'] == 'botTalk':
        return submission['phrases']
    elif submission['type'] == 'pronunciations':
        return submission['words']
    elif submission['type'] == 'speakOutLoud':
        return submission['sentences']
    return False

def add_to_bank(submission):
    if submission['type'] == 'video':
        question_data['questions'].append({
            "id": len(question_data['questions']) + 1,
            "type": "video",
            "content": submission['content'],
            "questions": submission['questions'],
            "path": submission['path']
        })
    elif submission['type'] == 'botTalk':
        question_data['questions'].append({
            "id": len(question_data['questions']) + 1,
            "type": "botTalk",
            "phrases": submission['phrases'],
            "path": submission['path']
        })
    elif submission['type'] == 'pronunciations':
        question_data['questions'].append({
            "id": len(question_data['questions']) + 1,
            "type": "pronunciations",
            "words": submission['words'],
            "path": submission['path']
        })
    elif submission['type'] == 'speakOutLoud':
        question_data['questions'].append({
            "id": len(question_data['questions']) + 1,
            "type": "speakOutLoud",
            "sentences": submission['sentences'],
            "path": submission['path']
        })

    # Save the updated data back to the JSON file
    with open('questions.json', 'w', encoding='utf-8') as qf:
        json.dump(question_data, qf, ensure_ascii=False, indent=4)

# Automated Verification and Addition
if st.button("Verify and Add All Submissions"):
    for submission in submissions:
        if verify_submission(submission):
            add_to_bank(submission)
    # Clear submissions after adding them to the bank
    open('submissions.json', 'w').close()
    st.success("All valid submissions verified and added to the bank!")

st.write("Submissions to be verified")
for submission in submissions:
    st.write(submission)
