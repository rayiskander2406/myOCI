FROM python:3.11-alpine

# Set timezone to Cairo
ENV TZ=Africa/Cairo

# Create non-root user first
RUN adduser -D -u 1000 ntfy

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy forwarder script and set ownership
COPY --chown=ntfy:ntfy forwarder.py .
RUN chmod +x forwarder.py

# Run as non-root user
USER ntfy

CMD ["python3", "/app/forwarder.py"]
