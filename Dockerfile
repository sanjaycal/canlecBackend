# Use the official Python 3.13 lightweight image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and keep stdout/stderr unbuffered
# This is highly recommended for containerized Python apps
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app/

# Install the dependencies directly from your pyproject.toml
RUN pip install --no-cache-dir .

# Cloud Run dynamically assigns a port via the PORT environment variable (usually 8080)
EXPOSE 8080

# Start the FastAPI app using Uvicorn
# We use sh -c to ensure the PORT environment variable is evaluated correctly
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
