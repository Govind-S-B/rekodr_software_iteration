import os
import json
import requests

# GENERAL COMPONENETS DEFINE HERE

def transcriber_wrapper(buffer_data,api_key):
    # Define the URL for the Deepgram API endpoint
    url = "https://api.deepgram.com/v1/listen?model=whisper-large"

    # Define the headers for the HTTP request
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/*"
    }

    # Since buffer_data is already in memory, we can directly send it in the request
    response = requests.post(url, headers=headers, data=buffer_data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        transcribe = response.json()
        # Extract the transcribed text
        transcribed_str = transcribe.get('results').get('channels')[0].get('alternatives')[0].get('transcript')
    else:
        # Handle errors (you might want to customize this part)
        raise Exception(f"Deepgram API request failed with status code {response.status_code}")

    return transcribed_str

def llm_wrapper(prompt,api_key):
    
    output_string = ""

    endpoint = 'https://api.groq.com/openai/v1/chat/completions'

    response = requests.post(
    url=endpoint,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },                
    json={
        "model": "llama3-70b-8192",
        "max_tokens": 6000,
        "temperature": 0.2,
        "messages": [
            {
                "content": prompt,
                "role": "user"
            }
        ]
    },)

    if response.status_code == 200:
        content = response.json()
        output_string =  content["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Request failed with status code {response.status_code}")

    return output_string

def embedding_wrapper(input_string,api_key):


    ENDPOINT_URL = "https://api.together.xyz/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "input": input_string,
        "model": "BAAI/bge-large-en-v1.5"
    }

    response = requests.post(ENDPOINT_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        embedding = response_data.get("data", [])[0].get("embedding", [])
    else:
        raise ValueError(f"Error: {response.status_code}")

    return embedding

