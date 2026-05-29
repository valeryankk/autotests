from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class CommonPgForm(BasePage):

    enterprise_field = (By.ID, "select_1")      
    forecast_field = (By.ID, "select_2")         
    year_field = (By.ID, "select_3")                  

    create_button = (By.XPATH, "//button[contains(@class, 'btn') and contains(@class, 'btn-secondary') and contains(@class, 'mr-1') and normalize-space(text())='Создать']")

    def select_first_from_autocomplete(self, locator):
        # Кликаем по полю, чтобы открыть список
        field = self.wait_until_clickable(locator)
        field.click()

        first_option = self.wait_until_clickable((By.XPATH, "//li[.//span[normalize-space(text()) != '']]"))
        first_option.click()

    def select_from_autocomplete(self, locator, value, enter_text=True):
        # Если нужно вводить текст — вводим, иначе просто кликаем по полю, чтобы открыть список
        element = self.wait_until_clickable(locator)
        element.click()
        
        if enter_text:
            element.send_keys(value)
        
        # Ждем появления нужного варианта и кликаем по нему
        option_locator = (By.XPATH,  f"//li[.//span[contains(text(), '{value}')]]") 
        self.wait_until_clickable(option_locator).click()

    def is_create_button_displayed(self):
        return self.is_element_displayed(self.create_button)

    def is_create_button_enabled(self):
        button = self.find(self.create_button)
        return button.is_enabled()

    def click_create_button(self):
        self.click(self.create_button)

    def fill_enterprise(self, value):
        self.select_from_autocomplete(self.enterprise_field, value)

    def fill_forecast(self, value):
        self.select_from_autocomplete(self.forecast_field, value)

    def fill_year(self, value):
        self.select_from_autocomplete(self.year_field, value)

 

