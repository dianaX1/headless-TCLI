FROM python:3.11-slim

# Install required system packages and build tools
RUN apt-get update && apt-get install -y \
    git cmake g++ make zlib1g-dev libssl-dev wget unzip

# Build TDLib from source
RUN git clone --depth 1 https://github.com/tdlib/tdlib.git && \
    mkdir -p tdlib/build && cd tdlib/build && \
    cmake .. && cmake --build . --target tdjson

# Set working directory
WORKDIR /app
COPY . .

# Set LD_LIBRARY_PATH for TDLib
ENV LD_LIBRARY_PATH=/tdlib/build

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["bash", "start.sh"]