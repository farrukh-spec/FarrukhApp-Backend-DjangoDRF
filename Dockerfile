# Use the official Python image
FROM python:3.13-slim

# Set environment variables so Python doesn't buffer output (better logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for mysqlclient or psycopg2)
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project code
COPY . .

# Make the script executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Run collectstatic (important for WhiteNoise)
RUN python manage.py collectstatic --noinput

# Start the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]