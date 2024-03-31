import pika
import json
import external_components

def summarize():
    pass

def embedd():
    pass

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

    transcript = external_components.transcriber_wrapper(audio_buffer)

    print(transcript)


    # transcribe the audio file

    # save the transcript to the database

    # summarize the transcript

    # save the summary to the database

    # embedd summary into vector db

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