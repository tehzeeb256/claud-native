# image

FORM python:3.12-slim   

# Environment

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 

# working directory 
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  

# copy project 
COPY app/ ./app

# security 
RUN useradd -m -u 1001 appuser
USER appuser
