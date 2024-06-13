import streamlit as st
import json
import os

# Load the question and video data from JSON files
with open('questions.json', encoding='utf-8') as qf:
    question_data = json.load(qf)

with open('videos.json', encoding='utf-8') as vf:
    video_data = json.load(vf)

# Function to save submissions temporarily
def save_submission(submission):
    with open('submissions.json', 'a', encoding='utf-8') as sf:
        json.dump(submission, sf, ensure_ascii=False, indent=4)
        sf.write('\n')

# Admin Page
st.title("Admin Page")

st.sidebar.title("Submit Content")
path_type = st.sidebar.selectbox("Path Type", ["quiz", "video", "botTalk", "pronunciations", "speakOutLoud"])

if path_type == "quiz":
    question = st.sidebar.text_input("Question")
    correct_answer = st.sidebar.text_input("Correct Answer")
    if st.sidebar.button("Submit"):
        submission = {
            "type": "quiz",
            "content": question,
            "correct_answer": correct_answer,
            "path": "quiz"
        }
        save_submission(submission)
        st.sidebar.success("Submitted successfully!")

elif path_type == "video":
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
with open('submissions.json', 'r', encoding='utf-8') as sf:
    submissions = sf.readlines()
    for submission in submissions:
        st.write(json.loads(submission))

# Function to verify and add submissions to the bank
def verify_submission(submission):
    # Example criteria: Ensure all fields are filled
    if submission['type'] == 'quiz':
        return submission['content'] and submission['correct_answer']
    elif submission['type'] == 'video':
        return submission['content'] and submission['questions'][0]['question'] and submission['questions'][0]['correct_answer']
    elif submission['type'] == 'botTalk':
        return submission['phrases']
    elif submission['type'] == 'pronunciations':
        return submission['words']
    elif submission['type'] == 'speakOutLoud':
        return submission['sentences']
    return False

def add_to_bank(submission):
    if submission['type'] == 'quiz':
        question_data['questions'].append({
            "id": len(question_data['questions']) + 1,
            "type": "text",
            "content": submission['content'],
            "correct_answer": submission['correct_answer'],
            "path": submission['path']
        })
    elif submission['type'] == 'video':
        video_data['videos'].append({
            "id": len(video_data['videos']) + 1,
            "url": submission['content'],
            "title": f"Video {len(video_data['videos']) + 1}",
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

    # Save the updated data back to the JSON files
    with open('questions.json', 'w', encoding='utf-8') as qf:
        json.dump(question_data, qf, ensure_ascii=False, indent=4)
    with open('videos.json', 'w', encoding='utf-8') as vf:
        json.dump(video_data, vf, ensure_ascii=False, indent=4)

# Automated Verification and Addition
if st.button("Verify and Add All Submissions"):
    with open('submissions.json', 'r', encoding='utf-8') as sf:
        submissions = sf.readlines()
        for submission in submissions:
            submission_data = json.loads(submission)
            if verify_submission(submission_data):
                add_to_bank(submission_data)
    # Clear submissions after adding them to the bank
    open('submissions.json', 'w').close()
    st.success("All valid submissions verified and added to the bank!")

st.write("Submissions to be verified")
with open('submissions.json', 'r', encoding='utf-8') as sf:
    submissions = sf.readlines()
    for submission in submissions:
        st.write(json.loads(submission))
