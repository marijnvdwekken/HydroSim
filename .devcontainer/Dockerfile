FROM mcr.microsoft.com/devcontainers/python:3.12

# System tooling required for building some Python wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies for the EPANET app and local debugging
COPY .devcontainer/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspaces/HydroSim
