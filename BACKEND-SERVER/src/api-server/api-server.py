from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime , inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import pika
import json
import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(
    name="transcripts",
    metadata={"hnsw:space": "cosine"},
)

# Define SQLAlchemy models
Base = declarative_base()

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now())
    path = Column(String)
    transcript_text = Column(String)  # New field

# Initialize FastAPI app
app = FastAPI()

# Initialize SQLAlchemy engine and session
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    publish_message(transcript.id)  # Publish message after commit
    db.close()

    return {"message": "File uploaded successfully"}


@app.post("/transcript/{audio_id}")
async def write_transcript_text(audio_id: int, transcript_text: str):
    db = SessionLocal()
    transcript = db.query(Transcript).filter(Transcript.id == audio_id).first()
    if transcript:
        transcript.transcript_text = transcript_text
        db.commit()
        db.close()
        return {"message": "Transcript text updated successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/transcript/{audio_id}")
async def get_transcript_text(audio_id: int):
    db = SessionLocal()
    transcript = db.query(Transcript).filter(Transcript.id == audio_id).first()
    db.close()
    if transcript:
        return {"transcript_text": transcript.transcript_text}
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@app.post("/transcript/{audio_id}/embedding")
async def store_transcript_embedding(audio_id: int, embedding: List[float]):
    db = SessionLocal()
    transcript = db.query(Transcript).filter(Transcript.id == audio_id).first()
    if transcript:
        metadata = {"timestamp": transcript.timestamp.isoformat()}
        chroma_collection.add(
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(audio_id)],
        )
        db.close()
        return {"message": "Transcript embedding stored successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Audio file not found")
    
@app.post("/transcript/search")
async def search_transcripts(query_embedding: List[float], top_n: int = 3, start_timestamp: Optional[str] = None, end_timestamp: Optional[str] = None):
    filters = {}
    if start_timestamp:
        filters["$gte"] = start_timestamp
    if end_timestamp:
        filters["$lte"] = end_timestamp

    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["metadatas", "ids"],
        where={
            "metadata": {
                "timestamp": filters,
            }
        },
    )

    transcript_ids = [int(result["ids"][0]) for result in results]
    db = SessionLocal()
    transcripts = db.query(Transcript).filter(Transcript.id.in_(transcript_ids)).all()
    db.close()

    transcript_data = [
        {
            "id": transcript.id,
            "timestamp": transcript.timestamp.isoformat(),
            "path": transcript.path,
            "transcript_text": transcript.transcript_text,
        }
        for transcript in transcripts
    ]

    return transcript_data

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
            "transcript_text": transcript.transcript_text,
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
