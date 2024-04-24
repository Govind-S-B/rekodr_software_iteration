import telebot
from telebot import types
import json
from io import BytesIO
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
from pydub import AudioSegment

load_dotenv(".env")
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

UID = None

@bot.message_handler(commands=['start'])
def start_handler(message):
    global UID
    UID = message.chat.id


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        voice_file_id = message.voice.file_id

        # Use the file ID to download the voice message
        voice_info = bot.get_file(voice_file_id)
        voice_file = bot.download_file(voice_info.file_path)

        buffer_data = BytesIO(voice_file)

        # Convert the audio to MP3
        audio = AudioSegment.from_file(buffer_data, format="ogg")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"{timestamp}.mp3"
        mp3_buffer = BytesIO()
        audio.export(mp3_buffer, format="mp3")
        mp3_buffer.seek(0)

        # Define the URL of your endpoint
        upload_url = "http://localhost:8000/upload/"

        # Prepare the files and data to send
        files = {'audio_file': (filename, mp3_buffer)}
        params = {'timestamp': timestamp}

        # Make the POST request to upload the file
        response = requests.post(upload_url, files=files, params=params)

        # Check the response
        if response.status_code == 200:

            # This response could be rich according to our new architecture


            bot.reply_to(message, "Voice message uploaded successfully.")
        else:
            bot.reply_to(message, "Failed to upload voice message.")

    except Exception as e:
        print(f"Exception: {e}")
        bot.reply_to(message, "An error occurred while processing your voice message.")

bot.infinity_polling()
