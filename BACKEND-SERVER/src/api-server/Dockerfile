FROM python:3.9-slim-bookworm

# Needed to build hnswlib during pip install. 
# See here https://github.com/chroma-core/chroma/issues/642
RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api-server:app", "--host", "0.0.0.0", "--port", "8000"]
