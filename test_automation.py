from selenium_automation import TaskAutomation
import os
from dotenv import load_dotenv

def test_automation():
    # Load environment variables
    load_dotenv()
    
    # Sample task details
    task_details = {
        "name": "Test Task",
        "type": "Task",
        "parent": "Parent Task",
        "allocation": "Allocation",
        "project_sequence": "1",
        "assignee": "User",
        "resource_sequence": "0",
        "hours": "01:00",
        "is_billable": True
    }
    
    try:
        # Initialize automation with credentials from .env file
        automation = TaskAutomation(
            base_url=os.getenv('GOODBOOKS_URL'),
            username=os.getenv('GOODBOOKS_USERNAME'),
            password=os.getenv('GOODBOOKS_PASSWORD')
        )
        
        # Run automation steps
        print("Logging in...")
        automation.login()
        
        print("Navigating to task creation...")
        automation.navigate_to_task_creation()
        
        print("Creating task...")
        automation.create_task(task_details)
        
        print("Task created successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if 'automation' in locals():
            automation.driver.quit()

if __name__ == "__main__":
    test_automation()