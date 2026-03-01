#!/bin/bash
echo "Setting up PromptDoctor PRO environment..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Setup complete! Run 'streamlit run src/app.py' to start the app."
