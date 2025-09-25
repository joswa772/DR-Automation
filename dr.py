import os
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
import logging

# Load .env variables
load_dotenv()
URL = os.getenv("URL")
SERVER = os.getenv("SERVER")
EMPCODE = os.getenv("EMPCODE")
PASSWORD = os.getenv("PASSWORD")

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(filename='logs/punch_log.txt', level=logging.INFO, 
                   format='%(asctime)s %(levelname)s: %(message)s')

# Load .env variables
load_dotenv()
URL = os.getenv("URL")
SERVER = os.getenv("SERVER")
EMPCODE = os.getenv("EMPCODE")
PASSWORD = os.getenv("PASSWORD")

def create_new_task(task_name, parent_name, allocation_name, project_sequence, resource_sequence, hours, is_billable, requester_name):
    """
    Create a new task with the specified details.
    
    Args:
        task_name (str): Name of the task
        parent_name (str): Name of the parent task
        allocation_name (str): Name of the allocation
        project_sequence (int): Project sequence number
        resource_sequence (int): Resource sequence number
        hours (str): Hours in HH:MM format
        is_billable (bool): Whether the task is billable
        requester_name (str): Name of the requester employee
    """
    options = Options()
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)
        print("🌐 Opened login page.")
        time.sleep(5)

        driver.find_element(By.NAME, "dbname").clear()
        driver.find_element(By.NAME, "dbname").send_keys(SERVER)
        driver.find_element(By.NAME, "userName").clear()
        driver.find_element(By.NAME, "userName").send_keys(EMPCODE)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//button[contains(text(),'LOGIN')]").click()
        print("🔓 Login submitted.")
        wait.until(EC.url_changes(URL))
        print("✅ Login successful. URL changed.")
        time.sleep(20)

        grid_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@id='modules']")))
        grid_icon.click()
        print("🧭 Clicked grid/menu launcher.")
        time.sleep(2)

        # Wait for the dynamic module menu to appear
        wait.until(EC.presence_of_element_located((By.ID, "dynmodule")))
        
        # Find and click the Projects module
        projects_li = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='dynmodule']//li[contains(.,'Project')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", projects_li)
        time.sleep(1)
        projects_li.click()
        print("📂 Clicked Projects module.")
        time.sleep(2)

        # Click on Transaction in the Project module
        transaction = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[span[normalize-space(text())='Transaction']]")
        ))
        transaction.click()
        print("📂 Clicked Transaction")
        time.sleep(2)

        # Click on Task under Transaction
        task = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[normalize-space(text())='Task']")
        ))
        task.click()
        print("� Clicked Task")
        time.sleep(2)

        # Wait for page to load and click the green plus button
        print("Looking for Add button...")
        add_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'btn-green') and contains(@onclick, 'addnewserviceForTask')]")
        ))
        add_button.click()
        print("➕ Clicked Add button")
        time.sleep(2)

         # Wait for task creation form
        print("📝 Filling task details...")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-content')]")
        ))

        # Fill in Task Name
        task_name_elem = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'select2-choice')]/span[contains(@class, 'select2-chosen') and contains(text(), 'Task Name')]")
        ))
        task_name_elem.click()
        task_name_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.select2-input")
        ))
        task_name_input.send_keys(task_name)
        task_name_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select Parent Name
        parent_dropdown = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'select2-chosen') and text()='Select Parent Name']")
        ))
        parent_dropdown.click()
        parent_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.select2-input")
        ))
        parent_input.send_keys(parent_name)
        parent_input.send_keys(Keys.RETURN)
        time.sleep(1)

        # Select Allocation Name
        allocation_dropdown = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'select2-chosen') and text()='Select Allocation Name']")
        ))
        allocation_dropdown.click()
        allocation_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.select2-input")
        ))
        allocation_input.send_keys(allocation_name)
        allocation_input.send_keys(Keys.RETURN)
        time.sleep(1)

        # Fill Project Sequence
        project_sequence_input = wait.until(EC.presence_of_element_located(
            (By.ID, "ProjectSequence")
        ))
        project_sequence_input.clear()
        project_sequence_input.send_keys(str(project_sequence))

        # Resource Sequence
        resource_sequence_input = wait.until(EC.presence_of_element_located(
            (By.ID, "ResourceSequence")
        ))
        resource_sequence_input.clear()
        resource_sequence_input.send_keys(str(resource_sequence))

        # Task Planned Hours
        hours_input = wait.until(EC.presence_of_element_located(
            (By.ID, "TaskPlannedHours")
        ))
        hours_input.clear()
        hours_input.send_keys(hours)

        # Is Billable checkbox
        billable_checkbox = wait.until(EC.presence_of_element_located(
            (By.ID, "IsBillable")
        ))
        if is_billable:
            if not billable_checkbox.is_selected():
                billable_checkbox.click()
        else:
            if billable_checkbox.is_selected():
                billable_checkbox.click()

        # Select Requester
        requester_dropdown = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'select2-chosen') and text()='Select Employee Name']")
        ))
        requester_dropdown.click()
        requester_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.select2-input")
        ))
        requester_input.send_keys(requester_name)
        requester_input.send_keys(Keys.RETURN)
        time.sleep(1)

        print("✅ All task details filled successfully")
        print("⏳ Waiting for confirmation...")
        time.sleep(2)

        # Find and click the Save button
        save_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='btnTaskSave']")
        ))
        save_button.click()
        print("💾 Save button clicked")

        # Wait for save confirmation
        time.sleep(5)  # Adjust this time based on how long the save operation typically takes


    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"screenshots/error_{timestamp}.png")
        print(f"❌ Site Punch FAILED at {datetime.now().strftime('%Y-%m-%d %H:%M')}\nError: {str(e)}")
    finally:
        driver.quit()
        logging.info('Browser closed.')


if __name__ == "__main__":
    # Example usage:
    task_details = {
        "task_name": "Example Task",
        "parent_name": "Parent Task",
        "allocation_name": "Project Allocation",
        "project_sequence": 1,
        "resource_sequence": 1,
        "hours": "01:00",
        "is_billable": True,
        "requester_name": "John Doe"
    }
    
    # Replace the values in task_details with actual values before running
    create_new_task(**task_details)

