#!/bin/bash

set -e

PROJECT_DIR="/root/portfolio"

echo "Changing into portfolio directory"
cd "${PROJECT_DIR}"

echo "Fetching latest changes from GitHub"
git fetch && git reset origin/main --hard

echo "Running docker compose down"
docker compose -f docker-compose.prod.yml

echo "Restarting with docker compose up"
docker compose -f docker-compose.prod.yml up -d --build

echo "Deployment successful!"
