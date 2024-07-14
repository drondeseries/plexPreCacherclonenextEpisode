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
COPY config.ini ./config.ini

# Install rclone and any other dependencies
RUN apt-get update \
    && apt-get install -y rclone cron \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PLEX_URL="http://localhost:32400" \
    PLEX_TOKEN="xxxxxxxxxxxx" \
    LOG_FILE="/app/logs/app.log" \
    CONFIG_LOCATION="/app/config.ini" \
    RCLONE_CONFIG="/root/.config/rclone/rclone.conf"

# Add cron job with configurable schedule
ENV SCRIPT_INTERVAL="*/15 * * * *"
RUN echo "$SCRIPT_INTERVAL /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/script-cron \
    && chmod 0644 /etc/cron.d/script-cron \
    && crontab /etc/cron.d/script-cron \
    && touch /var/log/cron.log

# Ensure the start script is executable
RUN chmod +x /start.sh

# Run the start script as the default command
CMD ["/start.sh"]
