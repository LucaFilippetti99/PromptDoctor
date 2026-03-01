@echo off
echo Setting up PromptDoctor PRO environment...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Setup complete! Run 'streamlit run src/app.py' to start the app.
pause
