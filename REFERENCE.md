**API Reference Documentation**

**1. File Upload Endpoint**
- Endpoint: `/upload/`
- Method: `POST`
- Description: Upload an audio file and timestamp.
- Request Parameters:
  - `timestamp` (str): The timestamp associated with the audio file.
  - `audio_file` (file): The audio file to be uploaded.
- Response:
  - `200 OK`: `{"message": "File uploaded successfully"}`
  - `400 Bad Request`: If the request is malformed or missing required parameters.

**2. Write Transcript Text Endpoint**
- Endpoint: `/transcript/{audio_id}`
- Method: `POST`
- Description: Write the transcript text for a given audio file.
- Path Parameters:
  - `audio_id` (int): The ID of the audio file.
- Request Body:
  - `transcript_text` (str): The transcript text to be written.
- Response:
  - `200 OK`: `{"message": "Transcript text updated successfully"}`
  - `404 Not Found`: If the audio file with the given `audio_id` is not found.

**3. Get Transcript Text Endpoint**
- Endpoint: `/transcript/{audio_id}`
- Method: `GET`
- Description: Retrieve the transcript text for a given audio file.
- Path Parameters:
  - `audio_id` (int): The ID of the audio file.
- Response:
  - `200 OK`: `{"transcript_text": "<transcript_text>"}`
  - `404 Not Found`: If the audio file with the given `audio_id` is not found.

**4. Store Transcript Embedding Endpoint**
- Endpoint: `/transcript/{audio_id}/embedding`
- Method: `POST`
- Description: Store the embedding for a given audio file transcript.
- Path Parameters:
  - `audio_id` (int): The ID of the audio file.
- Request Body:
  - `embedding` (List[float]): The embedding vector for the transcript.
- Response:
  - `200 OK`: `{"message": "Transcript embedding stored successfully"}`
  - `404 Not Found`: If the audio file with the given `audio_id` is not found.

**5. Search Transcripts Endpoint**
- Endpoint: `/transcript/search`
- Method: `POST`
- Description: Search for similar transcripts based on a query embedding and optional timestamp filters.
- Request Body:
  - `query_embedding` (List[float]): The embedding vector for the query.
  - `top_n` (int, optional): The number of top results to return (default: 3).
  - `start_timestamp` (str, optional): The start timestamp for filtering results (ISO format).
  - `end_timestamp` (str, optional): The end timestamp for filtering results (ISO format).
- Response:
  - `200 OK`: A list of matching transcripts with the following fields:
    - `id` (int): The ID of the transcript.
    - `timestamp` (str): The timestamp of the transcript (ISO format).
    - `path` (str): The file path of the audio file.
    - `transcript_text` (str): The transcript text.

**6. Get Audio Sample List Endpoint**
- Endpoint: `/debug/list`
- Method: `GET`
- Description: Retrieve a list of all audio files with their metadata.
- Response:
  - `200 OK`: A list of audio file metadata with the following fields:
    - `id` (int): The ID of the transcript.
    - `timestamp` (str): The timestamp of the transcript (ISO format).
    - `path` (str): The file path of the audio file.
    - `transcript_text` (str): The transcript text.

**7. Get Audio File Endpoint**
- Endpoint: `/debug/audio/{audio_id}`
- Method: `GET`
- Description: Retrieve an audio file by its ID.
- Path Parameters:
  - `audio_id` (int): The ID of the audio file.
- Response:
  - `200 OK`: The audio file content.
  - `404 Not Found`: If the audio file with the given `audio_id` is not found.

**8. Initialize Database Tables Endpoint**
- Endpoint: `/debug/initialize-db/`
- Method: `POST`
- Description: Initialize the database tables (debug endpoint).
- Response:
  - `200 OK`: `{"message": "Database tables initialized successfully"}`
  - `400 Bad Request`: If the database tables already exist.

**Database and Data Management Documentation**

This application uses a relational database (SQLite by default) to store the metadata and transcript text of audio files. The database schema consists of a single table called `transcripts` with the following columns:

- `id` (Integer, Primary Key, Index): The unique identifier for the transcript.
- `timestamp` (DateTime): The timestamp associated with the audio file.
- `path` (String): The file path of the audio file.
- `transcript_text` (String): The transcript text of the audio file.

The application also uses ChromaDB, a vector database, to store and search for transcript embeddings. The embeddings are stored along with the corresponding timestamp metadata in the ChromaDB collection named `transcripts`.

**Data Management**

1. **Audio File Upload**: When an audio file is uploaded via the `/upload/` endpoint, the file is saved to the `AUDIO_DATA_DIR` directory specified in the environment variables. The file path, along with the provided timestamp, is stored in the `transcripts` table of the relational database.

2. **Transcript Text Management**: The transcript text for an audio file can be written using the `/transcript/{audio_id}` endpoint (POST method) and retrieved using the same endpoint (GET method).

3. **Transcript Embedding Storage**: The embedding for a transcript can be stored in the ChromaDB collection using the `/transcript/{audio_id}/embedding` endpoint. The embedding vector and the corresponding timestamp metadata are added to the `transcripts` collection in ChromaDB.

4. **Transcript Search**: The `/transcript/search` endpoint allows searching for similar transcripts based on a query embedding. Optionally, timestamp filters can be applied to narrow down the search results. The endpoint retrieves the top `n` similar transcripts from ChromaDB and fetches the full transcript data from the relational database.

5. **Debug Endpoints**: The application includes two debug endpoints:
   - `/debug/list`: Retrieves a list of all audio files with their metadata and transcript text from the relational database.
   - `/debug/audio/{audio_id}`: Retrieves a specific audio file by its ID from the file system.
   - `/debug/initialize-db/`: Initializes the database tables (drops and recreates the `transcripts` table if it already exists).

6. **Message Queue Integration**: The application uses RabbitMQ as a message queue. When a new entry is added to the `transcripts` table in the relational database, a message with the transcript ID is published to the `db_entries` queue. This integration allows for further processing or notification of new transcript data.

It's important to note that the application assumes the presence of environment variables `DATABASE_URL` (for the relational database connection string) and `AUDIO_DATA_DIR` (for the directory where audio files are stored). Additionally, a running RabbitMQ instance is required for the message queue integration to work.