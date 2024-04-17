# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /personal_dashboard
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install .

EXPOSE XXXX

HEALTHCHECK CMD curl --fail http://localhost:XXXX/_stcore/health

ENTRYPOINT ["streamlit", "run", "Homepage.py", "--server.port=XXXX", "--server.address=0.0.0.0"]