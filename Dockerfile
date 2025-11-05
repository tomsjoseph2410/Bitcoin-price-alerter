FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Uncomment the following line to copy the config for local testing
# COPY config.yaml ./config.yaml

# Set the default command
CMD ["python", "src/main.py"]
