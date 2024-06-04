from openai import OpenAI
import os
import base64
from dotenv import load_dotenv
from sentence_transformers import util
import tempfile

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_answer(messages, system_prompt):
    system_message = [{"role": "system", "content": system_prompt}]
    messages = system_message + messages
    response = client.Completion.create(
        model="text-davinci-003",
        messages=messages
    )
    return response.choices[0].message.content

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = tempfile.mktemp(suffix=".mp3")
    with open(webm_file_path, "wb") as f:
        response.with_streaming_response().write_to_file(f)
    return webm_file_path

def semantic_similarity(user_answer, expected_answer, model):
    embeddings1 = model.encode(user_answer, convert_to_tensor=True)
    embeddings2 = model.encode(expected_answer, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
    return cosine_scores.item()
