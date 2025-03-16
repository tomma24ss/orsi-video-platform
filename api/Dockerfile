# Use Python base image
FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Install dependencies and upgrade pip
RUN pip install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose the API port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
