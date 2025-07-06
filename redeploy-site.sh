#!/bin/bash

# kill all tmux sessions
tmux kill-server

# cd into project directory

cd mlh-week1

# run git commands
git fetch && git reset origin/main --hard

# enter the python virtual environment and install python dependencies

source .venv/bin/activate
pip install -r requirements.txt

# start a new detached tmux session
cd ..
deactivate

tmux new-session -d -s portfolio
tmux send-keys -t portfolio "cd mlh-week1 && source .venv/bin/activate && flask run --host=0.0.0.0" C-m
