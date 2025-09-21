#!/bin/bash

# Path to your virtual environment
VENV_PATH="myenv/bin/activate"

# First terminal: start FastAPI server
gnome-terminal -- bash -c "source $VENV_PATH && uvicorn main:app --host 0.0.0.0 --port 8000 --reload; exec bash"

# Second terminal: run admin.py
gnome-terminal -- bash -c "source $VENV_PATH && python3 admin.py; exec bash"

