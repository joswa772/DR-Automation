from selenium_automation import TaskAutomation
from dotenv import load_dotenv
import os

def main():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env
    base_url = os.getenv('GOODBOOKS_URL')
    username = os.getenv('GOODBOOKS_USERNAME')
    password = os.getenv('GOODBOOKS_PASSWORD')
    
    print(f"URL configured: {base_url}")
    print(f"Username configured: {'Yes' if username else 'No'}")
    print(f"Password configured: {'Yes' if password else 'No'}")
    
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
        print("\nInitializing automation...")
        automation = TaskAutomation(base_url, username, password)
        
        print("Logging in...")
        automation.login()
        
        print("Navigating to task creation...")
        automation.navigate_to_task_creation()
        
        print("Creating task...")
        automation.create_task(task_details)
        
        print("\nTask creation completed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if 'automation' in locals():
            print("\nClosing browser...")
            automation.driver.quit()

if __name__ == "__main__":
    main()