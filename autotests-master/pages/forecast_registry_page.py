#реестр/окно подтверждения удаления/уведомления 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from selenium.common.exceptions import StaleElementReferenceException

class ForecastRegistryPage(BasePage):
    registry_container = (By.CSS_SELECTOR, "div.ag-center-cols-container")
    forecast_item_locator = (By.CSS_SELECTOR, "div.ag-center-cols-container > div")
    success_alert = (By.XPATH, "//div[contains(@class, 'message') and contains(@class, 'success')]//p[normalize-space()='Версия прогноза успешно создана']")
    delete = (By.CSS_SELECTOR, 'ui-button#delete button') # в реестре 
    edit_btn = (By.CSS_SELECTOR, 'ui-button#edit button') # в реестре 
    confirm_win = (By.XPATH, "//app-spark-confirm-form[contains(@class, 'modal')]")
    confirm_text = (By.XPATH, "//div[contains(@class, 'modal-body')]//span")
    cancel_delete_btn = (By.ID, 'confirmFormDeclineButton') # в окне подтверждения
    confirm_delete_btn = (By.ID, 'confirmFormConfirmButton') # в окне подтверждения
    
    success_delete_alert = (By.XPATH,"//div[contains(@class, 'message') and contains(@class, 'success')]//p[contains(text(), 'успешно удалена')]")
    success_edit_alert = (By.XPATH,"//div[contains(@class, 'message') and contains(@class, 'success')]//p[contains(text(), 'успешно отредактирована')]")
    create_button = (By.XPATH, "//button[contains(@class, 'btn') and contains(@class, 'btn-secondary') and contains(@class, 'mr-1') and normalize-space(text())='Создать']")
    lock = (By.XPATH, "//div[@role='gridcell' and (@title='Недоступно для редактирования' or @title='Доступно для редактирования')]")


    def reset_table_scroll(self): #после взаимодествия с реестром, происходит скролл. Метод возвращает этот скролл обратно.
        self.driver.execute_script("""
            const container = document.querySelector('.ag-center-cols-viewport');
            if (container) container.scrollLeft = 0;
        """)
        self.wait_until_visible(self.lock)

    def wait_for_forecast_to_appear_in_list(self, name, timeout=10):
        try:
            self.reset_table_scroll()
            container = self.wait.until(
                EC.visibility_of_element_located(self.registry_container)
            )
            WebDriverWait(self.driver, timeout).until(
                lambda d: any(name in el.text for el in container.find_elements(*self.forecast_item_locator))
            )
            return True
        except Exception:
            return False
        
    def wait_until_forecast_disappears(self, name, timeout=15): #Ожидает, пока версия прогноза с указанным именем исчезнет из таблицы
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self._is_forecast_missing(name)
            )
            return True
        except TimeoutException:
            raise AssertionError(f"Версия прогноза '{name}' не исчезла из списка в течение {timeout} секунд")

    def _is_forecast_missing(self, name):
        try:
            elements = self.driver.find_elements(*self.forecast_item_locator)
            return all(name != el.text for el in elements)
        except StaleElementReferenceException:
            return False


    def is_forecast_present(self, name): #Проверяет, что версия прогноза с указанным именем присутствует в списке
        try:
            container = self.driver.find_element(*self.registry_container)
            items = container.find_elements(*self.forecast_item_locator)
            return any(name in item.text for item in items)
        except Exception:
            return False

            
    def is_forecast_first_in_list(self, name):
        try:
            container = self.driver.find_element(*self.registry_container)
            items = container.find_elements(*self.forecast_item_locator)
            if not items:
                return False
            return name in items[0].text
        except Exception:
            return False
        
    def delete_forecast_by_name(self, name):
        try:
            self.close_all_modals_if_present()
            container = self.driver.find_element(*self.registry_container)
            items = container.find_elements(*self.forecast_item_locator)
            target_item = next((item for item in items if name in item.text), None)
            if target_item:
                target_item.click()
                self.reset_table_scroll()
                self.click_extra(self.delete)
                self.wait_until_clickable(self.confirm_delete_btn).click()# Подтверждаем удаление 
        except Exception as e:
            raise AssertionError(f"Ошибка при удалении прогноза '{name}': {e}")
    
    def select_first_forecast(self):
        """
        Находит первую версию в реестре и возвращает её имя из ячейки col-id="name".
        """
        container = self.wait_until_visible(self.registry_container)
        items = container.find_elements(*self.forecast_item_locator)

        for item in items:
            item.click()
            self.reset_table_scroll()

            # Ищем только ячейку с col-id="name"
            name_cell = item.find_element(By.CSS_SELECTOR, 'div[col-id="name"]')
            version_name = name_cell.text.strip()

            if version_name:
                return version_name

        raise Exception("Не найдена версия с непустым именем")
            

    def select_forecast_by_name(self, name):
        container = self.wait_until_visible(self.registry_container)
        items = container.find_elements(*self.forecast_item_locator)
        for item in items:
            if name in item.text:
                item.click()
                self.reset_table_scroll()
                return True
        raise AssertionError(f"Версия прогноза '{name}' не найдена в списке")        
    
    def find_first_non_empty_fluid_model_version_name(self, fluid_model_page): 
        """
        Находит первую версию в реестре, у которой вкладка 'Модели флюида' непустая.
        Возвращает имя этой версии.
        """
        container = self.wait_until_visible(self.registry_container)
        items = container.find_elements(*self.forecast_item_locator)
        
        for item in items:
            item.click()
            self.reset_table_scroll()

            # Ищем только ячейку с col-id="name"
            name_cell = item.find_element(By.CSS_SELECTOR, 'div[col-id="name"]')
            version_name = name_cell.text

            if not version_name:
                continue
            
            if fluid_model_page.is_fluid_model_list_not_empty():
                return version_name

        raise Exception("Не найдена версия с непустыми моделями флюида")


