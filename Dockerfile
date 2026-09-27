# image

FROM python:3.12-slim   

# Environment

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 

# working directory 
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  

# security 
RUN useradd -m -u 1001 appuser
USER appuser

# copy project 
COPY --chown=appuser:appuser app/ ./app

# user switch 
USER appuser

# port
EXPOSE 8000

# container start command 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
