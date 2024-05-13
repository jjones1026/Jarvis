from openai import OpenAI
import time
from pathlib import Path
from pygame import mixer
import time
import os
from dotenv import load_dotenv, find_dotenv

# Load .env file
load_dotenv()

# Access the API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

tts_enabled = True

# Initialize the client
client = OpenAI()
mixer.init()

# Create the assistant
date_and_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
context = """
    You are an assistant named Jarvis like from the ironman movies. 
    You are to act like him and provide help as best you can.  
    Be funny and witty. Keep it brief and serious. 
    Be a little sassy in your responses. 
    You have a variety of smart devices to control. 
    You can control them by ending your sentence with #light1-off like this. 
    Only use commands like this if I tell you to do so. nd your sentence with #lamp-1 for on and #lamp-0 for off. 
    Response in less than 80 words. 
    """ + date_and_time
assistant = client.beta.assistants.create(
    model="gpt-3.5-turbo-0125",
    name="Jarvis",
    instructions=context,
)

# Create empty thread for conversation
thread = client.beta.threads.create()

# Create function for conversation with memory
def ask_question_memory(question):
    global thread
    global thread_message
    thread_message = client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=question,
        )
    # Create a run for the thread using the defined assistant
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
    )
    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
          thread_id=thread.id,
          run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            return "The run failed."
        time.sleep(1)  # Wait for 1 second before checking again
    # Retrieve messages after the run has succeeded
    messages = client.beta.threads.messages.list(
      thread_id=thread.id
    )
    return messages.data[0].content[0].text.value

# Function to ask a question to the assistant with an image
def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()
    
# Function to generate TTS for each sentence and play them
def TTS(text):
    speech_file_path = Path(f"speech.mp3")
    speech_file_path = generate_tts(text, speech_file_path)
    play_sound(speech_file_path)
    while mixer.music.get_busy():  # Wait for the mixer to finish
        time.sleep(1)
    mixer.music.unload()
    # Delete the file after playing
    os.remove(speech_file_path)

    return "done"
            

# Function to generate TTS and return the file path
def generate_tts(sentence, speech_file_path):
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=sentence,
    )
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)
