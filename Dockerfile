FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY circuitbreaker/ ./circuitbreaker/
COPY policies.yaml .

# Expose port for API (future)
EXPOSE 8000

# Run as non-root user
RUN useradd -m -u 1000 circuitbreaker
USER circuitbreaker

CMD ["python", "-c", "from circuitbreaker import CircuitBreaker; print('CircuitBreaker ready')"]