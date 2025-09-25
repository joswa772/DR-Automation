from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
# from PIL import Image
import io
import uuid

load_dotenv()
URL = os.getenv("GOODBOOKS_URL")
SERVER = os.getenv("SERVER")
EMPCODE = os.getenv("GOODBOOKS_USERNAME")
PASSWORD = os.getenv("GOODBOOKS_PASSWORD")        

class TaskAutomation:
    def __init__(self, base_url, username, password):
        # Configure Firefox for headed mode
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        self.base_url = base_url
        self.username = username
        self.password = password
        self.screenshots = {}
        
        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options
        )
        self.driver.maximize_window()


    def login(self):
        print(f"Navigating to {self.base_url}")
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 20)  # Increased wait time
        
        # Capture login page
        time.sleep(5)  # Wait for page to stabilize
        self.capture_screenshot("login_page")
        
        print("Looking for login elements...")
        
        # Try different possible selectors for username field
        username_selectors = [
            (By.ID, "username"),
            (By.NAME, "username"),
            (By.NAME, "user"),
            (By.ID, "user"),
            (By.CSS_SELECTOR, "input[type='text']")
        ]
        
        password_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']")
        ]
        
        # Try to find username field
        username_field = None
        for by, selector in username_selectors:
            try:
                username_field = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"Found username field with selector: {selector}")
                break
            except:
                continue
        
        if not username_field:
            raise Exception("Could not find username field")
            
        # Try to find password field
        password_field = None
        for by, selector in password_selectors:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"Found password field with selector: {selector}")
                break
            except:
                continue
                
        if not password_field:
            raise Exception("Could not find password field")
        
        print("Entering credentials...")
        username_field.clear()
        username_field.send_keys(self.username)
        password_field.clear()
        password_field.send_keys(self.password)
        
        # Try different possible login button selectors
        login_button_selectors = [
            (By.XPATH, "//button[contains(text(), 'LOGIN')]"),
            (By.XPATH, "//button[contains(text(), 'Log In')]"),
            (By.XPATH, "//input[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']")
        ]
        
        login_button = None
        for by, selector in login_button_selectors:
            try:
                login_button = wait.until(EC.element_to_be_clickable((by, selector)))
                print(f"Found login button with selector: {selector}")
                break
            except:
                continue
                
        if not login_button:
            raise Exception("Could not find login button")
            
        print("Clicking login button...")
        login_button.click()
        
        # Capture logged-in homepage
        self.capture_screenshot("logged_in_home")

    def navigate_to_task_creation(self):
        wait = WebDriverWait(self.driver, 20)  # Increased wait time
        
        print("Waiting for page to load after login...")
        time.sleep(5)  # Give the page time to fully load
        
        # Capture main menu
        self.capture_screenshot("main_menu")
        print("Looking for Projects menu...")
        
        # Try different selectors for Projects
        project_selectors = [
            "//div[text()='Projects']",
            "//div[contains(text(),'Project')]",
            "//a[contains(text(),'Project')]",
            "//span[contains(text(),'Project')]"
        ]
        
        projects_module = None
        for selector in project_selectors:
            try:
                projects_module = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                print(f"Found Projects menu with selector: {selector}")
                break
            except:
                continue
                
        if not projects_module:
            # Print current page source for debugging
            print("Could not find Projects menu. Current page content:")
            print(self.driver.page_source[:500])  # Print first 500 chars
            raise Exception("Could not find Projects menu")
            
        print("Clicking Projects menu...")
        projects_module.click()
        time.sleep(2)  # Wait for menu to expand
        
        print("Looking for Transaction menu...")
        transaction_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Transaction']")))
        print("Clicking Transaction menu...")
        transaction_menu.click()
        time.sleep(2)  # Wait for menu to expand
        
        print("Looking for Task option...")
        task_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Task']")))
        print("Clicking Task option...")
        task_option.click()
        
        # Capture task list
        print("Loading task list...")
        time.sleep(2)  # Wait for page to load
        self.capture_screenshot("task_list")

    def create_task(self, task_details):
        wait = WebDriverWait(self.driver, 10)
        
        # Capture task list before adding
        self.capture_screenshot("before_adding_task")
        
        # Click the '+' to create new task
        add_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Add']")))
        add_button.click()
        
        # Capture task creation form
        self.capture_screenshot("task_creation_form")
        
        # Fill form fields
        self._fill_form_fields(task_details)
        
        # Capture filled form
        self.capture_screenshot("filled_form")
        
        # Save task
        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]")))
        save_button.click()
        
        # Capture success confirmation
        self.capture_screenshot("task_saved")

    def _fill_form_fields(self, details):
        # Name field
        name_field = self.driver.find_element(By.NAME, "name")
        name_field.clear()
        name_field.send_keys(details["name"])
        
        # Type dropdown
        type_dropdown = self.driver.find_element(By.NAME, "type")
        type_dropdown.click()
        type_option = self.driver.find_element(By.XPATH, f"//option[text()='{details['type']}']")
        type_option.click()
        
        # Parent task
        parent_dropdown = self.driver.find_element(By.NAME, "parent")
        parent_dropdown.click()
        parent_option = self.driver.find_element(By.XPATH, f"//option[text()='{details['parent']}']")
        parent_option.click()
        
        # Allocation
        allocation_dropdown = self.driver.find_element(By.NAME, "allocation")
        allocation_dropdown.click()
        allocation_option = self.driver.find_element(By.XPATH, f"//option[text()='{details['allocation']}']")
        allocation_option.click()
        
        # Project sequence
        project_sequence_field = self.driver.find_element(By.NAME, "project_sequence")
        project_sequence_field.clear()
        project_sequence_field.send_keys(details["project_sequence"])
        
        # Assignee
        assignee_dropdown = self.driver.find_element(By.NAME, "assignee")
        assignee_dropdown.click()
        assignee_option = self.driver.find_element(By.XPATH, f"//option[text()='{details['assignee']}']")
        assignee_option.click()
        
        # Resource sequence
        resource_sequence_field = self.driver.find_element(By.NAME, "resource_sequence")
        resource_sequence_field.clear()
        resource_sequence_field.send_keys(details["resource_sequence"])
        
        # Hours
        hours_field = self.driver.find_element(By.NAME, "hours")
        hours_field.clear()
        hours_field.send_keys(details["hours"])
        
        # Is Billable checkbox
        is_billable_checkbox = self.driver.find_element(By.NAME, "is_billable")
        if details["is_billable"]:
            is_billable_checkbox.click()

    def capture_screenshot(self, step_name):
        """Capture screenshot and store in memory"""
        img = self.driver.get_screenshot_as_png()
        self.screenshots[step_name] = img

    def get_screenshots(self):
        """Get all captured screenshots"""
        return self.screenshots.copy()

    def close(self):
        self.driver.quit()

# For testing purposes
if __name__ == "__main__":
    # Sample task details for testing
    test_details = {
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
    
    # Initialize automation with credentials from environment variables
    automation = TaskAutomation(
        base_url=URL,
        username=EMPCODE,
        password=PASSWORD
    )
    
    try:
        print("Starting automation process...")
        print("Logging in...")
        automation.login()
        
        print("Navigating to task creation...")
        automation.navigate_to_task_creation()
        
        print("Creating task...")
        automation.create_task(test_details)
        
        print("Task created successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        print("Closing browser...")
        automation.close()
