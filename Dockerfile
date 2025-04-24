# Start with Python base image
FROM python:3.10-slim

# Set port for the container
EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Set working directory and copy all project files
WORKDIR /app
COPY . /app

# Create non-root user and change ownership
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Start the app using Gunicorn and your app instance
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "FplLeague:app"]
