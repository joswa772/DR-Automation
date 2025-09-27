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
from selenium.webdriver.common.keys import Keys
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
        
        # Click Projects Module
        projects_li = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[@id='dynmodule']//li[contains(.,'Project')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", projects_li)
        time.sleep(1)
        projects_li.click()
        print("📂 Clicked Projects module")
        time.sleep(2)

        # Click Transaction
        transaction = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[span[normalize-space(text())='Transaction']]")
        ))
        transaction.click()
        print("📂 Clicked Transaction")
        time.sleep(2)

        # Click Task
        task = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space(text())='Task']")
        ))
        task.click()
        print("📋 Clicked Task")
        time.sleep(5)  # Wait for task screen to load

        # Wait for page to load and click the green plus button
        print("Looking for Add button...")
        add_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'btn-green') and contains(@onclick, 'addnewserviceForTask')]")
        ))
        add_button.click()
        print("➕ Clicked Add button")
        time.sleep(3)  # Wait for form to load
        
        # Wait for task creation form
        print("📝 Filling task details...")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-content')]")
        ))

        def fill_select2_input(dropdown_text, value):
            """Helper function to fill select2 inputs reliably"""
            # Find and click the dropdown
            dropdown = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//span[contains(@class,'select2-chosen') and contains(text(),'{dropdown_text}')]")
            ))
            dropdown.click()
            time.sleep(2)  # Increased wait for dropdown to open

            # Wait for and find the input field
            input_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".select2-drop-active input.select2-input")
            ))
            input_field.clear()
            time.sleep(1)  # Wait after clearing
            
            # Type the value
            for char in value:
                input_field.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)  # Wait after typing

            # Press Enter and wait for selection
            input_field.send_keys(Keys.RETURN)
            time.sleep(2)  # Increased wait after selection

            # Wait for dropdown to close
            wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))
            time.sleep(1)  # Additional wait after dropdown closes
            
            # Click somewhere else to ensure the dropdown is fully closed
            body = driver.find_element(By.TAG_NAME, "body")
            body.click()
            time.sleep(1)
            
            print(f"✓ Filled {dropdown_text} with '{value}'")

        print("Filling Task Name...")
        fill_select2_input("Task Name", task_name)
        
        # Helper for select2 fields by label
        def fill_select2_by_label(label_text, value):
            # Find the label
            label_elem = wait.until(EC.presence_of_element_located((By.XPATH, f"//label[contains(normalize-space(.),'{label_text}') or contains(normalize-space(.),'{label_text}*')]")))
            # Go up to the parent row/container
            parent_row = label_elem.find_element(By.XPATH, './ancestor::*[self::div or self::td or self::tr][1]')
            # Find the first select2 container in that row after the label
            containers = parent_row.find_elements(By.XPATH, ".//span[contains(@class,'select2-container')]")
            # Heuristic: pick the rightmost if label is on left, or first after label
            container = None
            for c in containers:
                if c.location['x'] > label_elem.location['x']:
                    container = c
                    break
            if not container and containers:
                container = containers[-1]
            if not container:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                os.makedirs('screenshots', exist_ok=True)
                driver.save_screenshot(f'screenshots/parent_container_not_found_{ts}.png')
                raise Exception(f"Could not find select2 container for '{label_text}' in row")
            driver.execute_script("arguments[0].scrollIntoView(true);", container)
            try:
                container.click()
            except Exception:
                driver.execute_script("arguments[0].click();", container)
            time.sleep(0.5)
            # Try multiple selectors for the input
            input_selectors = [
                '.select2-drop-active input.select2-input',
                '.select2-drop input.select2-input',
                'input.select2-input',
                '.select2-search input',
            ]
            input_field = None
            for sel in input_selectors:
                try:
                    input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                    break
                except Exception:
                    continue
            if not input_field:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                driver.save_screenshot(f'screenshots/parent_input_not_found_{ts}.png')
                raise Exception(f"Could not find select2 input for '{label_text}'")
            input_field.clear()
            for ch in value:
                input_field.send_keys(ch)
                time.sleep(0.05)
            time.sleep(0.5)
            # Try to click the matching result
            try:
                opt = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class,'select2-result-label') and normalize-space(text())='{value}']")))
                opt.click()
            except Exception:
                input_field.send_keys(Keys.RETURN)
            wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, 'select2-drop-active')))
            time.sleep(0.3)
            print(f"✓ {label_text} set to '{value}'")

        # Step-by-step for each circled field
        print("Selecting Parent Name...")
        fill_select2_by_label('Parent', parent_name)

        print("Selecting Requester...")
        fill_select2_by_label('Employee Name', requester_name)


        print("Selecting Activity...")
        try:
            from task_input import TASK_DETAILS
            activity_val = TASK_DETAILS.get('activity_name', '')
        except Exception:
            activity_val = ''
        fill_select2_by_label('Activity Name', activity_val)

        print("Selecting Allocation Name...")
        fill_select2_by_label('Allocation Name', allocation_name)


        print("Selecting Allocation Split...")
        try:
            from task_input import TASK_DETAILS
            alloc_split_val = TASK_DETAILS.get('allocation_split', '')
        except Exception:
            alloc_split_val = ''
        try:
            fill_select2_by_label('Allocation Split', alloc_split_val)
        except Exception:
            print("(Optional) Allocation Split not set or not present.")

        print("Setting Project Sequence...")
        project_sequence_input = wait.until(EC.presence_of_element_located((By.ID, "ProjectSequence")))
        project_sequence_input.clear()
        project_sequence_input.send_keys(str(project_sequence))
        time.sleep(0.3)

        print("Setting Hours...")
        hours_input = wait.until(EC.presence_of_element_located((By.ID, "TaskPlannedHours")))
        hours_input.clear()
        hours_input.send_keys(hours)
        time.sleep(0.3)

        print("Setting Is Billable checkbox...")
        billable_checkbox = wait.until(EC.presence_of_element_located((By.ID, "IsBillable")))
        is_billable_val = str(is_billable).lower()
        if is_billable_val in ('yes', 'y', 'true', '1'):
            if not billable_checkbox.is_selected():
                billable_checkbox.click()
                print("✓ Checked the billable checkbox")
        else:
            if billable_checkbox.is_selected():
                billable_checkbox.click()
                print("✓ Unchecked the billable checkbox")
        time.sleep(0.3)

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
        print(f"❌ Error: {str(e)}")
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        # Take screenshot on error
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot(f"screenshots/error_{timestamp}.png")
    finally:
        driver.quit()
        logging.info('Browser closed')

if __name__ == "__main__":
    # Import task details from the input file
    from task_input import TASK_DETAILS
    
    print("\nTask Details from input file:")
    for key, value in TASK_DETAILS.items():
        print(f"{key}: {value}")
    print("\nCreating task with these details...\n")
    
    # Create the task with the details from task_input.py
    create_new_task(**TASK_DETAILS)