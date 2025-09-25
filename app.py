from flask import Flask, render_template, request, jsonify
from selenium_automation import TaskAutomation
import os
import json
import requests
import threading
from dotenv import load_dotenv

load_dotenv()  # Load credentials from .env

app = Flask(__name__)
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama endpoint

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Prompt Llama3 to detect task creation intent
    prompt = f"""
    You are a helpful assistant for GoodBooks task automation. 
    Analyze the user's message and:
    1. If it's a task creation request, extract:
       - Task name
       - Task type (task/work)
       - Mandatory fields: name, type, parent, allocation, project_sequence, assignee, hours, is_billable
    2. If not, respond naturally.
    
    User message: "{user_message}"
    """
    
    # Call Llama3
    response = requests.post(OLLAMA_API_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })
    
    if response.status_code != 200:
        return jsonify({"error": "Llama3 unavailable"}), 500
        
    llm_response = response.json().get('response', '')
    
    # Check if task creation is requested
    if "task_name" in llm_response.lower() or "create task" in llm_response.lower():
        # Extract task details (simplified parsing)
        task_details = extract_task_details(llm_response)
        if task_details:
            # Run automation in background
            thread = threading.Thread(target=create_task_async, args=(task_details,))
            thread.start()
            return jsonify({
                "response": "Creating task... Please wait.",
                "task_created": True
            })
    
    return jsonify({"response": llm_response})

def extract_task_details(response_text):
    """Naive extraction - replace with proper NLP parsing in production"""
    details = {}
    lines = response_text.split('\n')
    
    for line in lines:
        if "name:" in line.lower():
            details["name"] = line.split(":")[1].strip()
        elif "type:" in line.lower():
            details["type"] = line.split(":")[1].strip()
        # Add more fields as needed
    
    return details or None

def create_task_async(task_details):
    automation = TaskAutomation(
        base_url=os.getenv('GOODBOOKS_URL'),
        username=os.getenv('GOODBOOKS_USERNAME'),
        password=os.getenv('GOODBOOKS_PASSWORD')
    )
    
    try:
        automation.login()
        automation.navigate_to_task_creation()
        automation.create_task(task_details)
        print("Task created successfully!")
    except Exception as e:
        print(f"Automation error: {e}")
    finally:
        automation.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)  