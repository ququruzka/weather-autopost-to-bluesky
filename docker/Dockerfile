FROM python:3.11-slim

# Set working directory
WORKDIR /app

# TZ
RUN apt-get update && apt-get install -y tzdata
# Install cron
RUN apt-get install -y cron

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your autopost script to container
COPY auto_posting.py .
COPY .env .

# Add crontab file to schedule autoposting jobs
COPY crontab.txt /etc/cron.d/bluesky-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/bluesky-cron

# Apply the cron job
RUN crontab /etc/cron.d/bluesky-cron

# Create the log file for cron logs
RUN touch /var/log/cron.log

# Run cron in the foreground so container stays alive & logs output
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]
