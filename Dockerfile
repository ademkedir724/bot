# Dockerfile
FROM python:3.11-slim

# Prevents Python from writing pyc files to disc and forces stdin/stdout/stderr streams to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /app/app
COPY ./migrations /app/migrations

# The command to run the application will be specified in docker-compose.yml
# to allow for a startup script that waits for the DB and runs migrations.
# This CMD is a fallback for running the container directly.
CMD ["python", "-m", "app.main"]
