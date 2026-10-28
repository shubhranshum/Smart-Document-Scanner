FROM python:3.12-slim

# Install minimal OS libraries required by OpenCV headless and image decoders
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY . .

# Expose port (Render/Railway sets PORT dynamically via $PORT)
ENV PORT=8000
EXPOSE 8000

# Start Uvicorn ASGI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
