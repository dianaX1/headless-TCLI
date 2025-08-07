FROM python:3.11-slim

# Allow optional GitHub authentication via a token for non-interactive environments
ARG GITHUB_TOKEN=""
ENV GIT_TERMINAL_PROMPT=0

# Install required system packages and build tools
RUN apt-get update && apt-get install -y \
    git cmake g++ make zlib1g-dev libssl-dev wget unzip

# Build TDLib from source non-interactively with optional token authentication
RUN if [ -n "$GITHUB_TOKEN" ]; then \
      echo "Cloning TDLib repository with token authentication"; \
      git clone --depth 1 https://$GITHUB_TOKEN@github.com/tdlib/tdlib.git; \
    else \
      echo "Cloning TDLib repository without authentication"; \
      git clone --depth 1 https://github.com/tdlib/tdlib.git; \
    fi && \
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