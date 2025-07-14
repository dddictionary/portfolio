#!/bin/bash

set -e

PROJECT_DIR="/root/portfolio"

echo "Changing into portfolio directory"
cd "${PROJECT_DIR}"

# kill all tmux sessions
echo "Killing all existing tmux sessions"
tmux kill-server


# run git commands
echo "Fetching latest changes from GitHub"
git fetch && git reset origin/main --hard

# enter the python virtual environment and install python dependencies
echo "Activating virtual environment"
source .venv/bin/activate

echo "Installing packages"
pip install -r requirements.txt

# start a new detached tmux sessions
echo "Starting new tmux session"
tmux new-session -d -s portfolio
tmux send-keys -t portfolio "flask run --host=0.0.0.0" C-m
