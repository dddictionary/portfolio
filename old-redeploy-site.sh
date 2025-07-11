#!/bin/bash

session_name="flask_app"
venv_path="python3-virtualenv/bin/activate"
tmux kill-server || true
git fetch origin
git reset --hard origin/main
tmux new-session -d -s ${session_name}
tmux send-keys -t ${session_name} "source ${venv_path}" C-m
tmux send-keys -t ${session_name} "pip install -r requirements.txt" C-m
tmux send-keys -t ${session_name} "flask run --host=0.0.0.0" C-m
