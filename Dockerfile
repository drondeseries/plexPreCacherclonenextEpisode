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
COPY start.sh /start.sh
COPY config.ini ./config/config.ini
COPY plexrclonecache.log ./logs/plexrclonecache.log

# Install rclone and any other dependencies
RUN apt-get update \
    && apt-get install -y rclone cron \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the start script is executable
RUN chmod +x /start.sh

# Add cron job with configurable schedule
ENV SCRIPT_INTERVAL="*/20 * * * *"
RUN echo "$SCRIPT_INTERVAL /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/script-cron \
    && chmod 0644 /etc/cron.d/script-cron \
    && crontab /etc/cron.d/script-cron \
    && touch /var/log/cron.log

# Run the start script as the default command
CMD ["/start.sh"]
