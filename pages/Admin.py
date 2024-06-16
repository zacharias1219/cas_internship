import streamlit as st
import requests

# Ensure this URL is correct and accessible
API_URL = "http://127.0.0.1:5000"

def get_submissions():
    response = requests.get(f"{API_URL}/submissions")
    return response.json()

def save_submission(submission):
    response = requests.post(f"{API_URL}/submissions", json=submission)
    return response.json()

def delete_submission(index):
    response = requests.delete(f"{API_URL}/submissions/{index}")
    return response.json()

def add_to_bank(submission):
    response = requests.post(f"{API_URL}/questions", json=submission)
    return response.json()

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
        st.sidebar.success("Submitted successfully!")

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
        st.sidebar.success("Submitted successfully!")

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
        st.sidebar.success("Submitted successfully!")

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
        st.sidebar.success("Submitted successfully!")

st.write("Submissions")
submissions = get_submissions()
for i, submission in enumerate(submissions):
    st.write(submission)
    if st.button(f"Delete {i}", key=f"delete_{i}"):
        delete_submission(i)
        st.experimental_rerun()

if st.button("Verify and Add All Submissions"):
    valid_submissions = [submission for submission in submissions if submission]  # Simple check to ensure submission exists
    for submission in valid_submissions:
        add_to_bank(submission)
    # Clear valid submissions after adding them to the bank
    for i in range(len(submissions)-1, -1, -1):  # Iterate in reverse to avoid index shifting
        delete_submission(i)
    st.success("All valid submissions verified and added to the bank!")
    st.experimental_rerun()

st.write("Submissions to be verified")
for submission in submissions:
    st.write(submission)
