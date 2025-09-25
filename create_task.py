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
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Find and click the dropdown
                    dropdown = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//span[contains(@class,'select2-chosen') and contains(text(),'{dropdown_text}')]")
                    ))
                    time.sleep(1)  # Wait for any animations to complete
                    dropdown.click()
                    time.sleep(1)  # Wait for dropdown to open fully

                    # Wait for the select2 dropdown to be visible
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))
                    
                    # Find the input field in the active dropdown
                    input_field = driver.find_element(By.CSS_SELECTOR, ".select2-drop-active input.select2-input")
                    input_field.clear()
                    time.sleep(0.5)
                    
                    # Type the value character by character
                    for char in value:
                        input_field.send_keys(char)
                        time.sleep(0.1)
                    time.sleep(0.5)

                    if dropdown_text.strip().lower() == "task name":
                        # For Task Name, just press Enter to confirm new entry
                        input_field.send_keys(Keys.RETURN)
                        time.sleep(0.5)
                        # Ensure dropdown is closed
                        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))
                        # Release focus
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            body.send_keys(Keys.ESCAPE)
                            time.sleep(0.2)
                            body.click()
                            time.sleep(0.2)
                        except Exception:
                            pass
                        print(f"✓ Entered new {dropdown_text}: '{value}'")
                        return
                    else:
                        time.sleep(1)  # Wait for dropdown options to appear
                        # Look for the matching option and click it
                        try:
                            # First try exact match
                            option = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, f"//div[contains(@class, 'select2-result-label') and normalize-space(text())='{value}']")
                            ))
                        except:
                            # If exact match fails, try contains match
                            option = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, f"//div[contains(@class, 'select2-result-label') and contains(text(), '{value}')]")
                            ))
                        print(f"Found matching option: {option.text}")
                        option.click()
                        time.sleep(0.5)  # Wait for selection to complete
                        # Ensure dropdown is closed
                        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))
                        # Extra robustness: send ESCAPE and click body to release focus
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            body.send_keys(Keys.ESCAPE)
                            time.sleep(0.2)
                            body.click()
                            time.sleep(0.2)
                        except Exception:
                            pass
                        time.sleep(0.5)
                        print(f"✓ Successfully filled {dropdown_text} with '{value}'")
                        return
                    
                except Exception as e:
                    if attempt < max_attempts - 1:  # Don't print on last attempt
                        print(f"⚠️ Attempt {attempt + 1} failed for {dropdown_text}. Retrying...")
                        time.sleep(1)  # Wait before retrying
                        # Try to close any open dropdowns before retrying
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            body.send_keys(Keys.ESCAPE)
                            time.sleep(1)
                        except:
                            pass
                    else:
                        print(f"❌ Failed to fill {dropdown_text} after {max_attempts} attempts")
                        raise  # Re-raise the last exception
            # Find and click the dropdown
            dropdown = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//span[contains(@class,'select2-chosen') and contains(text(),'{dropdown_text}')]")
            ))
            time.sleep(1)  # Wait for any animations to complete
            dropdown.click()
            time.sleep(1)  # Wait for dropdown to open fully

            # Wait for the select2 dropdown to be visible
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))
            
            # Find the input field in the active dropdown
            input_field = driver.find_element(By.CSS_SELECTOR, ".select2-drop-active input.select2-input")
            input_field.clear()
            time.sleep(0.5)
            
            # Type the value character by character
            for char in value:
                input_field.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(1)  # Wait for dropdown options to appear
            
            # Press Enter to select the first matching option
            input_field.send_keys(Keys.RETURN)
            time.sleep(1)  # Wait for selection to complete
            
            # Wait for dropdown to close
            wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "select2-drop-active")))

        print("Filling Task Name...")
        fill_select2_input("Task Name", task_name)
        
        print("Selecting Parent Name...")
        fill_select2_input("Select Parent Name", parent_name)
        
        print("Selecting Allocation Name...")
        fill_select2_input("Select Allocation Name", allocation_name)

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
        print(f"Setting billable status to: {is_billable}")
        billable_checkbox = wait.until(EC.presence_of_element_located(
            (By.ID, "IsBillable")
        ))
        is_billable = str(is_billable).lower()  # Convert to lowercase string
        
        if is_billable == 'yes':
            # Check if it's not already checked
            if not billable_checkbox.is_selected():
                billable_checkbox.click()
                print("✓ Checked the billable checkbox")
        elif is_billable == 'no':
            # Uncheck if it's currently checked
            if billable_checkbox.is_selected():
                billable_checkbox.click()
                print("✓ Unchecked the billable checkbox")
        else:
            print(f"⚠️ Warning: Invalid billable value '{is_billable}'. Use 'yes' or 'no'.")

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