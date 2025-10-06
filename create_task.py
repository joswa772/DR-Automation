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

        # --- REVISED SECTION FOR CLICKING THE ADD BUTTON ---
        print("🔎 Looking for the 'Add' button...")
        try:
            # Wait up to 20 seconds for the button to be clickable
            add_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'btn-green') and contains(@onclick, 'addnewserviceForTask')]")
            ))
            print("✅ 'Add' button found and is clickable.")
            
            # Take a screenshot right before clicking for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/before_add_click_{timestamp}.png")
            print(f"📸 Saved screenshot before clicking 'Add' button.")

            # Standard click attempt
            add_button.click()
            print("➕ Clicked 'Add' button using standard click.")

        except Exception as e:
            print(f"⚠️ Standard click failed: {e}. Trying JavaScript click...")
            try:
                # Fallback: Find the element again and use JavaScript to click it
                add_button_js = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-green') and contains(@onclick, 'addnewserviceForTask')]")
                driver.execute_script("arguments[0].click();", add_button_js)
                print("➕ Successfully clicked 'Add' button using JavaScript.")
            except Exception as js_e:
                print(f"❌ JavaScript click also failed: {js_e}")
                # Take a screenshot of the failure state
                timestamp_fail = datetime.now().strftime("%Y%m%d_%H%M%S")
                driver.save_screenshot(f"screenshots/add_button_fail_{timestamp_fail}.png")
                print(f"📸 Saved failure screenshot. Halting execution.")
                logging.error(f"Could not click the 'Add' button. Error: {js_e}", exc_info=True)
                driver.quit()
                exit() # Exit the script if we can't proceed
        # --- END OF REVISED SECTION ---

        print("⏳ Waiting for the task creation form to load...")
        # Increased wait time for the form modal to appear
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-content')]")
        ))
        print("✅ Task creation form is now visible.")

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
            
            print(f"✓ Filled {dropdown_text} with '{value}'")

        # Fill Task Name
        print("Filling Task Name...")
        fill_select2_input("Task Name", task_name)
        
        # Fill Parent Name
        print("Filling Parent Name...")
        fill_select2_input("Select Parent Name", parent_name)

        # Fill Allocation Name
        print("Filling Allocation Name...")
        fill_select2_input("Select Allocation Name", allocation_name)

        # Fill Project Sequence
        print("Setting Project Sequence...")
        project_sequence_input = wait.until(EC.presence_of_element_located((By.ID, "ProjectSequence")))
        project_sequence_input.clear()
        project_sequence_input.send_keys(str(project_sequence))
        time.sleep(0.3)

        # Fill Incharge (Resource)
        print("Filling Incharge...")
        # This field appears to be already selected with "Joswa" in the HTML, but we'll update it if needed
        try:
            incharge_dropdown = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(@class,'select2-chosen') and contains(.,'Joswa')]/ancestor::a[contains(@class,'select2-choice')]")
            ))
            incharge_dropdown.click()
            time.sleep(2)
            
            input_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".select2-drop-active input.select2-input")
            ))
            input_field.clear()
            time.sleep(1)
            
            # Type the value (assuming we have an incharge parameter, otherwise use the default)
            incharge_value = "Joswa"  # Default value, could be parameterized
            for char in incharge_value:
                input_field.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)
            
            input_field.send_keys(Keys.RETURN)
            time.sleep(2)
            print(f"✓ Filled Incharge with '{incharge_value}'")
        except Exception as e:
            print(f"⚠️ Could not update Incharge field: {str(e)}")

        # Fill Resource Sequence
        print("Setting Resource Sequence...")
        resource_sequence_input = wait.until(EC.presence_of_element_located((By.ID, "ResourceSequence")))
        resource_sequence_input.clear()
        resource_sequence_input.send_keys(str(resource_sequence))
        time.sleep(0.3)

        # Fill Hours
        print("Setting Hours...")
        hours_input = wait.until(EC.presence_of_element_located((By.ID, "TaskPlannedHours")))
        hours_input.clear()
        hours_input.send_keys(hours)
        time.sleep(0.3)

        # Set Is Billable checkbox
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

        # Fill Requester
        print("Filling Requester...")
        fill_select2_input("Select Employee Name", requester_name)

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