# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy package metadata and requirements
COPY pyproject.toml requirements.txt ./

# Copy source code
COPY src/ ./src/

# Install dependencies and the package
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Default command
CMD ["airbnb-ops", "run"]
