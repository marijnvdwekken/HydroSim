# Dockerfile

# Use a base Python image
FROM python:3.12-slim

# Install epyt
RUN pip install epyt

# Install pymodbus
RUN pip install pymodbus paho-mqtt python-dotenv

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Give execute permission to the entrypoint script
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]
