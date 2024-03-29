import requests
from datetime import datetime

# Define the endpoint URL
url = 'http://localhost:8000/upload/'

# Get the current timestamp
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Load the audio file
audio_file_path = './sample-audios/test.mp3'  # Change this to the path of your audio file

# Open and read the audio file in binary mode
with open(audio_file_path, 'rb') as file:
    # Prepare the data payload for the request
    files = {'audio_file': ("test.mp3", file)}
    params = {'timestamp': current_time}

    # Send the POST request to the endpoint
    response = requests.post(url, files=files, params=params)

# Check the response
if response.status_code == 200:
    print("File uploaded successfully")
else:
    print("Failed to upload file:", response.text)