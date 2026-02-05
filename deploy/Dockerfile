FROM python:3.11-slim

# Install ffmpeg for pydub
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV API_KEY=replace_with_a_strong_api_key
ENV MODEL_PATH=app/artifacts/model.joblib

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
