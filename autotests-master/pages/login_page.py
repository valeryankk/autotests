from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class LoginPage:
    def __init__(self, driver, base_url, login_url):
        self.driver = driver
        self.base_url = base_url
        self.login_url = login_url

        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.signin_button = (By.ID, "kc-login")
        self.remember_me_checkbox = (By.ID, "rememberMe")
        self.error_message = (By.ID, "input-error")  

    def open(self):
        self.driver.get(self.login_url)

    def login(self, username, password):
        self.driver.find_element(*self.username_input).clear()
        
        self.driver.find_element(*self.username_input).send_keys(username)

        self.driver.find_element(*self.password_input).clear()

        self.driver.find_element(*self.password_input).send_keys(password)

        self.driver.find_element(*self.signin_button).click()

    def get_error_text(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.error_message)
        )
        return self.driver.find_element(*self.error_message).text
    
    def click_remember_me(self):
        self.driver.find_element(*self.remember_me_checkbox).click()

    def is_remember_me_selected(self):
        return self.driver.find_element(*self.remember_me_checkbox).is_selected()
        

    def is_element_displayed(self, locator):
        return self.driver.find_element(*locator).is_displayed()

    def is_button_enabled(self):
        return self.driver.find_element(*self.signin_button).is_enabled()
    
    def append_to_username(self, extra_text):
        elem = self.driver.find_element(*self.username_input)
        elem.send_keys(extra_text)

    def append_to_password(self, extra_text):
        elem = self.driver.find_element(*self.password_input)
        elem.send_keys(extra_text)
