FROM python:3.11-alpine

# Set timezone to match server
ENV TZ=Africa/Cairo

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY health_checker.py .
COPY config.yml .
COPY entrypoint.sh .

# Set permissions
RUN chmod +x health_checker.py entrypoint.sh

# Default command runs the health check in a loop (every 12 hours)
CMD ["/app/entrypoint.sh"]
