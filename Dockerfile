FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use unbuffered logging for better Render logs
ENV PYTHONUNBUFFERED=1

# Expose port (Render will override this with PORT env var)
EXPOSE 5000

# Improved Health check that respects PORT environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests, os; port = os.environ.get('PORT', '5000'); requests.get(f'http://localhost:{port}/health')"

# Run application with initialization first
# We use one worker for SQLite stability on Render
CMD python init_db.py && gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 app:app
