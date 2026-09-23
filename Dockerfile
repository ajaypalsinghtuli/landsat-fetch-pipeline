# Use the official lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing pyc files to disc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required for geospatial libraries (like shapely)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies and add Gunicorn for production serving
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

# Copy the rest of the application code
COPY . .

# Create the instance directory for SQLite and downloads inside the container
RUN mkdir -p instance/downloads

# Expose the port the app runs on
EXPOSE 5010

# Run the application using Gunicorn
# We use 1 worker with multiple threads to prevent SQLite database locking conflicts
CMD ["gunicorn", "--bind", "0.0.0.0:5010", "--workers", "1", "--threads", "4", "run:app"]