# Create virtual environment
python3 -m venv .venv

.venv\Scripts\activate

pip install flask selenium webdriver-manager requests python-dotenv 
python.exe -m pip install --upgrade pip

python app.py
