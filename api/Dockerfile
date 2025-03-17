# Use Python base image
FROM python:3.12-slim

# Set environment variables for PATH
ENV PATH="/root/.local/bin:$PATH"

# Create working directory
WORKDIR /app

# Install system dependencies and kubectl
RUN apt-get update && apt-get install -y \
    curl \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip



# Copy requirements and install them (with cache)
COPY requirements.txt .
RUN pip install --cache-dir=/root/.cache/pip -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the API port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
