from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TaskAutomation:
    def __init__(self, base_url, username, password):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        self.base_url = base_url
        self.username = username
        self.password = password

    def login(self):
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password"))))
        
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN')]")))
        login_button.click()

    def navigate_to_task_creation(self):
        wait = WebDriverWait(self.driver, 10)
        
        # Navigate to Projects → Transaction → Task
        projects_module = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Projects']")))
        projects_module.click()
        
        transaction_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Transaction']")))
        transaction_menu.click()
        
        task_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Task']")))
        task_option.click()

    def create_task(self, task_details):
        wait = WebDriverWait(self.driver, 10)
        
        # Click '+' to create new task
        add_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Add']")))
        add_button.click()
        
        # Fill form fields
        self._fill_form_fields(task_details)
        
        # Save task
        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]")))
        save_button.click()

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

    def close(self):
        self.driver.quit()