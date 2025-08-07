FROM python:3.11-slim

# Install required system packages (minimal set for tdjson package)
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
COPY . .

# Install Python dependencies (includes tdjson with pre-compiled TDLib)
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["bash", "start.sh"]
