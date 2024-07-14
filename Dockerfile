# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all Python files and requirements.txt into the container
COPY requirements.txt ./
COPY config.py ./
COPY disk.py ./
COPY logger.py ./
COPY plex_utils.py ./
COPY rclone.py ./
COPY main.py ./

# Install rclone
RUN apt-get update && apt-get install -y rclone

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variables
ENV PLEX_URL="http://localhost:32400"
ENV PLEX_TOKEN="xxxxxxxxxxxx"
ENV LOG_FILE="/app/logs/app.log"
ENV CONFIG_LOCATION="/app/config/config.ini"
ENV SCRIPT_INTERVAL=15
ENV RCLONE_CONFIG="/root/.config/rclone/rclone.conf"

# Run main.py when the container launches
CMD ["python", "main.py"]
