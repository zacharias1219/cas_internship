import streamlit as st
import json
import os

# Load the submission data from JSON file
def load_submissions():
    if os.path.exists('submissions.json'):
        with open('submissions.json', 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Save submissions to JSON file
def save_submissions(submissions):
    with open('submissions.json', 'w', encoding='utf-8') as file:
        json.dump(submissions, file, ensure_ascii=False, indent=4)

# Load existing submissions
submissions = load_submissions()

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
        submissions.append(submission)
        save_submissions(submissions)
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
        submissions.append(submission)
        save_submissions(submissions)
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
        submissions.append(submission)
        save_submissions(submissions)
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
        submissions.append(submission)
        save_submissions(submissions)
        st.sidebar.success("Submitted successfully!")

st.write("Submissions")
for i, submission in enumerate(submissions):
    st.write(submission)
    if st.button(f"Delete {i}", key=f"delete_{i}"):
        del submissions[i]
        save_submissions(submissions)
        st.experimental_rerun()
