FROM python:3.11-slim

# System update + Ghostscript install
RUN apt-get update && apt-get install -y ghostscript

# App directory
WORKDIR /app

# Project files copy
COPY . .

# Python dependencies install
RUN pip install -r requirements.txt

# Flask app start
CMD ["python", "app.py"]
