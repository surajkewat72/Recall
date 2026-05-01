# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create the chroma_db directory and set permissions
RUN mkdir -p /app/chroma_db && chmod 777 /app/chroma_db

# Expose the port Hugging Face expects (7860)
EXPOSE 7860

# Run the application
# We use 0.0.0.0 to bind to all interfaces and port 7860 for Hugging Face
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
