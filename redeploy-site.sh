#!/bin/bash

set -e

PROJECT_DIR="/root/portfolio"

echo "Changing into portfolio directory"
cd "${PROJECT_DIR}"

echo "Fetching latest changes from GitHub"
git fetch && git reset origin/main --hard

echo "Activating virtual environment"
source .venv/bin/activate

echo "Installing packages"
pip install -r requirements.txt

echo "Restarting service"
sudo systemctl restart myportfolio

echo "Checking service status"
sudo systemctl status myportfolio --no-pager

echo "Deployment successful!"
