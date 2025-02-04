#!/bin/bash

# Load environment variables
source .env

# Define main compose file
COMPOSE_FILES="docker-compose.yml"

# Conditionally add ppgserver configuration if INCLUDE_PPGSERVER is true
if [ "$INCLUDE_PPGSERVER" = "true" ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f ppgserver/docker-compose.ppgserver.yml"
fi

# Run docker-compose with the selected files and remove orphan containers
docker-compose -f $COMPOSE_FILES up -d --build --remove-orphans
