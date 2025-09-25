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
    
    # Generate task description using Ollama
    task_description = generate_task_description(user_message)
    
    if task_description:
        # Extract task details from generated description
        task_details = parse_task_details(task_description)
        
        if task_details:
            try:
                # Run automation in background
                thread = threading.Thread(target=lambda: selenium_automation.create_task_with_details(task_details))
                thread.start()
                return jsonify({
                    "response": "Creating task with the following details:\n" + 
                               "\n".join([f"{k}: {v}" for k, v in task_details.items()]),
                    "task_created": True,
                    "status": "processing"
                })
            except Exception as e:
                return jsonify({
                    "response": f"Error creating task: {str(e)}",
                    "task_created": False,
                    "status": "error"
                })
    
    return jsonify({
        "response": "I couldn't understand the task details. Please provide:\n" +
                   "- Task name\n" +
                   "- Task type\n" +
                   "- Parent task\n" +
                   "- Allocation\n" +
                   "- Project sequence\n" +
                   "- Assignee\n" +
                   "- Resource sequence\n" +
                   "- Hours\n" +
                   "- Is billable (yes/no)",
        "task_created": False,
        "status": "error"
    })

def generate_task_description(prompt):
    """Generate task description using Ollama"""
    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": "llama3",
            "prompt": f"Generate a detailed task description based on this request: {prompt}",
            "stream": False
        })
        
        if response.status_code == 200:
            return response.json().get('response', '')
        return None
    except Exception as e:
        print(f"Ollama error: {e}")
        return None

def parse_task_details(description):
    """Parse task details from Ollama-generated description"""
    # This would contain NLP logic to extract fields
    # For simplicity, returning sample data
    return {
        "name": "Sample Task",
        "type": "Task",
        "parent": "Parent Task",
        "allocation": "Allocation",
        "project_sequence": "1",
        "assignee": "User",
        "resource_sequence": "0",
        "hours": "01:00",
        "is_billable": True
    }

def create_task_with_screenshots(task_details):
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