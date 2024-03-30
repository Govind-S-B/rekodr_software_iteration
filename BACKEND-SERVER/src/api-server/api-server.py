from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime , inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Define SQLAlchemy models
Base = declarative_base()

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now())
    path = Column(String)

# Initialize FastAPI app
app = FastAPI()

# Initialize SQLAlchemy engine and session
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



import pika
import json

# Function to publish messages
def publish_message(id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='db_entries')
    channel.basic_publish(exchange='',
                          routing_key='db_entries',
                          body=json.dumps({'id': id}))
    connection.close()

# Endpoint to upload audio file and timestamp
@app.post("/upload/")
async def upload_file(timestamp: str, audio_file: UploadFile = File(...)):


    audio_dir = os.getenv("AUDIO_DATA_DIR")
    file_path = os.path.join(audio_dir, audio_file.filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())

    # Add entry to database
    db = SessionLocal()
    transcript = Transcript(timestamp=timestamp, path=file_path)
    db.add(transcript)
    db.commit()
    print("PUSHING TO QUEUE")
    publish_message(transcript.id)  # Publish message after commit
    print("PUSHED TO QUEUE")
    db.close()

    return {"message": "File uploaded successfully"}


@app.get("/debug/list")
async def get_random_audio_sample():
    db = SessionLocal()
    transcripts = db.query(Transcript).all()
    db.close()

    sample_data = [
        {
            "id": transcript.id,
            "timestamp": transcript.timestamp.isoformat(),
            "path": transcript.path,
        }
        for transcript in transcripts
    ]

    return sample_data

# Endpoint to retrieve audio file
@app.get("/debug/audio/{audio_id}")
async def get_audio(audio_id: int):
    db = SessionLocal()
    transcript = db.query(Transcript).filter(Transcript.id == audio_id).first()
    db.close()

    if transcript:
        file_path = transcript.path
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

# Endpoint to initialize database tables (debug endpoint)
@app.post("/debug/initialize-db/")
async def initialize_db():
    # Check if tables exist before creating them
    inspector = inspect(engine)
    if not inspector.has_table("transcripts"):
        Base.metadata.create_all(bind=engine)
        return {"message": "Database tables initialized successfully"}
    else:
        raise HTTPException(status_code=400, detail="Database tables already exist")
