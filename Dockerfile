# Use Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8001"]