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
from selenium.webdriver.firefox.service import Service
import logging

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(filename='logs/task_automation.txt', level=logging.INFO, 
                   format='%(asctime)s %(levelname)s: %(message)s')

# Load .env variables
load_dotenv()
URL = os.getenv("URL")
SERVER = os.getenv("SERVER")
EMPCODE = os.getenv("EMPCODE")
PASSWORD = os.getenv("PASSWORD")

def automate_task_creation(task_details=None):
    options = Options()
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)

    try:
        # Login
        driver.get(URL)
        print("🌐 Opened login page")
        time.sleep(5)

        driver.find_element(By.NAME, "dbname").clear()
        driver.find_element(By.NAME, "dbname").send_keys(SERVER)
        driver.find_element(By.NAME, "userName").clear()
        driver.find_element(By.NAME, "userName").send_keys(EMPCODE)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//button[contains(text(),'LOGIN')]").click()
        print("🔓 Login submitted")
        wait.until(EC.url_changes(URL))
        print("✅ Login successful")
        time.sleep(5)

        # Click Grid Menu
        grid_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@id='modules']")))
        grid_icon.click()
        print("🧭 Clicked grid menu")
        time.sleep(2)

        # Wait for dynamic module menu
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
        time.sleep(2)

        # Click Add button
        add_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@title='Add']")
        ))
        add_button.click()
        print("➕ Clicked Add button")
        time.sleep(2)

        # Wait for form to load
        form = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-content')]")
        ))
        print("📝 Task form loaded")

        print("✅ Navigation completed successfully")
        
        # Keep browser open for debugging
        input("Press Enter to close the browser...")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"screenshots/error_{timestamp}.png")
    finally:
        driver.quit()
        logging.info('Browser closed')

if __name__ == "__main__":
    automate_task_creation()