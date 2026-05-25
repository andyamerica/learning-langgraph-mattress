# Use a slim Python image for speed
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the orchestration script
COPY main.py .

# Run the script when the container starts
CMD ["python", "main.py"]