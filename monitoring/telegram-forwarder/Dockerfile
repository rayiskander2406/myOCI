FROM python:3.11-alpine

# Set timezone to Cairo
ENV TZ=Africa/Cairo

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy forwarder script
COPY forwarder.py .
RUN chmod +x forwarder.py

# Run as non-root user
RUN adduser -D -u 1000 ntfy
USER ntfy

CMD ["python3", "/app/forwarder.py"]
