#!/bin/bash

# Ensure no existing cron.pid file
rm -f /var/run/crond.pid

# Check if SCRIPT_INTERVAL is set
if [ -z "$SCRIPT_INTERVAL" ]; then
  echo "SCRIPT_INTERVAL is not set. Exiting."
  exit 1
fi

# Add cron job with configurable schedule
echo "$SCRIPT_INTERVAL /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/script-cron
chmod 0644 /etc/cron.d/script-cron
crontab /etc/cron.d/script-cron
touch /var/log/cron.log

# Start the cron daemon in the foreground
cron

# Check if the cron job was added
echo "Cron jobs:"
crontab -l

# Tail the cron log file to keep the container running
tail -f /var/log/cron.log
