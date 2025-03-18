FROM python:3.12-slim

WORKDIR /app

# Install basic system dependencies and ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy the application code
COPY . .

CMD ["python", "app.py"]
