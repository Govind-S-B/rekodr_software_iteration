import pika
import json
import external_components
import requests

from api_key_load_balancer import api_key_load_balancer
gkeys = api_key_load_balancer(path="./keys/google_keys.json")
tkeys = api_key_load_balancer(path="./keys/together_keys.json")
groqkeys = api_key_load_balancer(path="./keys/groq_keys.json")
deepgramkeys = api_key_load_balancer(path="./keys/deepgram_keys.json")

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"Received ID: {data['id']}")


    # load the audio file
    import os
    from io import BytesIO
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, Column, Integer, String, DateTime , inspect
    from datetime import datetime
    from sqlalchemy.ext.declarative import declarative_base

    # Define SQLAlchemy models
    Base = declarative_base()

    class Transcript(Base):
        __tablename__ = "transcripts"

        id = Column(Integer, primary_key=True, index=True)
        timestamp = Column(DateTime, default=datetime.now())
        path = Column(String)

    # Initialize SQLAlchemy engine and session
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Retrieve the path of the audio file from the database
    db = SessionLocal()
    transcript = db.query(Transcript).filter(Transcript.id == data['id']).first()
    db.close()

    if transcript:
        file_path = transcript.path
        # Load the audio file into a BytesIO buffer
        with open(file_path, 'rb') as audio_file:
            audio_buffer = BytesIO(audio_file.read())
    else:
        print(f"No transcript found for ID: {data['id']}")
        audio_buffer = None

    transcript_string = external_components.transcriber_wrapper(audio_buffer,deepgramkeys.get_key())

    embedding = external_components.embedding_wrapper(transcript_string,tkeys.get_key())

    # Send the transcript text to the API
    api_base_url = "http://fastapi-app:8000"  # Replace with the actual host and port of your API service

    transcript_endpoint = f"{api_base_url}/transcript/{data['id']}"
    transcript_response = requests.post(transcript_endpoint, json={"transcript_text": transcript_string})
    if transcript_response.status_code == 200:
        print("Transcript text added successfully")
    else:
        print(f"Failed to add transcript text: {transcript_response.text}")

    # Send the embedding to the API
    embedding_endpoint = f"{api_base_url}/transcript/{data['id']}/embedding"
    embedding_response = requests.post(embedding_endpoint, json={"embedding": embedding})
    if embedding_response.status_code == 200:
        print("Embedding added successfully")
    else:
        print(f"Failed to add embedding: {embedding_response.text}")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='db_entries')

    channel.basic_consume(queue='db_entries',
                          auto_ack=True,
                          on_message_callback=callback)

    channel.start_consuming()

if __name__ == '__main__':
    main()