# Use a Python base image
FROM python:3.9-slim as base

# Set environment variables
ENV DAPR_HOME=/home/dapr
ENV PATH=$DAPR_HOME/bin:$PATH
ENV COMPONENTS_PATH=/app/components
ENV APP_PORT=8000

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl gcc g++ && \
    curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE $APP_PORT

FROM base as leader
CMD ["uvicorn", "leader:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base as follower
CMD ["uvicorn", "follower:app", "--host", "0.0.0.0", "--port", "8000"]
