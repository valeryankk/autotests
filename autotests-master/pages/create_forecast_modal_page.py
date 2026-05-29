from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class CreateForecastVersionModal(BasePage):
    create_form = (By.CLASS_NAME, "modal-content")
    title = (By.XPATH, "//modal-container//app-version-create-form//h4")
    subtitle = (By.CSS_SELECTOR, "app-version-create-form .modal-body span")

    name_input = (By.ID, "projectFormNameInput")
    name_label = (By.XPATH, "//label[contains(text(), 'Наименование')]")

    creation_method_label = (By.XPATH, "//label[contains(text(), 'Способ создания')]")
    creation_method_field = (By.XPATH, "//label[contains(text(), 'Способ создания')]/following-sibling::div//input[contains(@class, 'custom-select') and @readonly]")

    creation_method_options = (By.XPATH, "//bs-dropdown-container//virtual-scroller//div[2]/li")
    json_file_input = (By.ID, "jsonFileInput") # для загрузки файла (ангуляр)
    json_file_label = (By.CSS_SELECTOR, "label.custom-file-label") # текст внутри инпута

    json_results_field = (By.ID, 'jsonFileCheckingResultTextArea')#поле результат проверки

    start_date_label = (By.XPATH, "//label[contains(text(), 'Дата начала расчета')]")
    start_date_field = (By.ID, "dateBegin")
    end_date_label = (By.XPATH, "//label[contains(text(), 'Дата конца расчета')]")
    end_date_field = (By.ID, "dateEnd")

    #внутри календаря
    calendar_popup = (By.CSS_SELECTOR, 'div.flatpickr-calendar.open')# Корневой контейнер календаря (появляется при клике на поле даты)
    calendar_year_input = (By.CSS_SELECTOR, "input[aria-label='Год']")# Инпут для выбора года (в календаре)
    calendar_month_dropdown = (By.CSS_SELECTOR, "select[aria-label='Month'][tabindex='-1']")
    calendar_left_arrow = (By.CSS_SELECTOR, 'span.flatpickr-prev-month')# Стрелка назад (предыдущий месяц)
    calendar_right_arrow = (By.CLASS_NAME, 'flatpickr-next-month')# Стрелка вперед (следующий месяц)
    calendar_year_next = (By.CSS_SELECTOR, 'span.arrowUp')# Стрелка вверх (следующий год)
    calendar_year_previous = (By.CSS_SELECTOR, 'span.arrowDown')# Стрелка вниз (предыдущий год)

    calc_step_label = (By.XPATH, "//label[contains(text(), 'Расчетный шаг')]")
    calc_step_field = (By.ID, "step") 
    calc_step_units_dropdown = (By.CSS_SELECTOR, 'input[ng-reflect-model="Месяц"]')

    report_detail_label = (By.XPATH, "//label[contains(text(), 'Детализация отчетов')]")
    report_detail_dropdown = (By.CSS_SELECTOR, 'input[ng-reflect-model="Каждый шаг"]')

    description_label = (By.XPATH, "//label[contains(text(), 'Описание')]")
    description_field = (By.ID, "favoriteFunctionDescriptionTextArea")

    lock_edit_checkbox = (By.CSS_SELECTOR, "label[for='disableVersionEditing']")
    edit_checkbox = (By.CSS_SELECTOR, "input[type='checkbox'][id='disableVersionEditing'][formcontrolname='isBlocked']")

    check_btn = (By.XPATH, "//button[contains(text(), 'Проверить')]")
    close_button = (By.XPATH, "//button[contains(text(), 'Отмена')]")
    close_cross = (By.XPATH, "//button[@aria-label='Close' and contains(@class, 'close')]")
    create_button2 = (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[normalize-space()='Создать']") # в форме
    save_button = (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[contains(text(), 'Сохранить') or contains(text(), 'Создать')]")
    

    main_version_lbl = (By.CSS_SELECTOR, "label[for='isDefault']")
    main_version_checkbox = (By.CSS_SELECTOR, "input[type='checkbox'][id='isDefault'][formcontrolname='isDefault']")

    #копирование версии
    copy_source_do_field = (By.XPATH, "//simpl-apps-select[@formcontrolname='enterprise']//input")
    copy_source_forecast_field = (By.XPATH, "//simpl-apps-select[@formcontrolname='forecastType']//input")
    copy_source_year_field = (By.XPATH, "//simpl-apps-select[@formcontrolname='year']//input")
    copy_source_version_field = (By.XPATH, "//simpl-apps-select[@formcontrolname='version']//input")
    combobox_locator = (By.XPATH, "//bs-dropdown-container//virtual-scroller//div[2]/li")

    def get_selected_month(self):
        select_elem = self.wait_until_visible((By.CSS_SELECTOR, "select.flatpickr-monthDropdown-months"))
        select = Select(select_elem)
        return select.first_selected_option.text.strip()

    def click_year_next(self):
        self.click_element_with_hover(self.calendar_year_input, self.calendar_year_next)

    def click_year_previous(self):
        self.click_element_with_hover(self.calendar_year_input, self.calendar_year_previous)

    @staticmethod # Выбор определённого дня в календаре (по тексту) 
    def calendar_day(day: str):
        return (By.XPATH, f"//span[contains(@class, 'flatpickr-day') and text()='{day}']")

    def calendar_month_option(month_name: str):
        return (By.XPATH, f"//select[contains(@class, 'flatpickr-monthDropdown-months')]/option[normalize-space(text())='{month_name}']")

    def wait_until_modal_visible(self):
        return self.wait_until_visible(self.create_form)

    def get_title_text(self):
        title_element = self.wait_until_visible(self.title)
        return title_element.text
    
    def get_subtitle_text(self):
        subtitle_element = self.wait_until_visible(self.subtitle)
        return subtitle_element.text
    
    def get_start_date(self):
        return self.wait_until_visible(self.start_date_field).get_attribute("value")

    def get_end_date(self):
        return self.wait_until_visible(self.end_date_field).get_attribute("value")

    def set_start_date(self, date_str):
        field = self.wait_until_visible(self.start_date_field)

        actions = ActionChains(self.driver)
        actions.move_to_element(field).click().pause(0.2)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).pause(0.2)  # выделяем всё
        actions.send_keys(date_str).pause(0.2)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    def set_end_date(self, date_str):
        field = self.wait_until_visible(self.end_date_field)

        actions = ActionChains(self.driver)
        actions.move_to_element(field).click().pause(0.2)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).pause(0.2)  # выделяем всё
        actions.send_keys(date_str).pause(0.2)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    # Проверка на недоступность (readonly или disabled)
    def is_field_readonly(self, locator):
        elem = self.wait_until_visible(locator)
        readonly = elem.get_attribute("readonly")
        disabled = elem.get_attribute("disabled")
        return readonly == "true" or disabled == "true"

    def get_field_value(self, locator):
        elem = self.wait_until_visible(locator)
        return elem.get_attribute("value")
    
    def close(self):
        close_button = (By.XPATH, "//button[contains(text(), 'Отмена')]")
        elem = self.wait_until_visible(close_button)
        elem.click()

    def is_create_btn_disabled(self): # кнопка создать в модалке 
        button = self.wait_until_visible(self.create_button2)
        disabled_attr = button.get_attribute("disabled")
        return disabled_attr is not None and disabled_attr != "false"
    
    def wait_until_modal_disappears(self):
        self.wait.until_not(EC.visibility_of_element_located(self.create_form))
    
    # для просмотра какой элемент перекрывает нужный
    def debug_overlay_element(self, locator):
        element = self.wait_until_visible(locator)
        rect = self.driver.execute_script("""
            const el = arguments[0];
            const rect = el.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const topElement = document.elementFromPoint(centerX, centerY);
            return {
                tag: topElement.tagName,
                class: topElement.className,
                id: topElement.id,
                outerHTML: topElement.outerHTML
            };
        """, element)
        print("Перекрывающий элемент:")
        print(rect["tag"], rect["id"], rect["class"])
        print(rect["outerHTML"][:500])  # Показать первые 500 символов HTML
        return rect
    
    def select_from_combobox(self, combobox_locator, option_text, options_locator):

        # Находим и кликаем по полю, чтобы раскрыть список
        field = self.wait_until_visible(combobox_locator)
        field.click()

        # Ждем появления всех опций
        options = self.wait_until_visible_all(options_locator)

        # Ищем нужную опцию по тексту и кликаем по ней
        for option in options:
            if option.text.strip() == option_text:
                assert option.is_enabled(), f"Опция '{option_text}' должна быть активна"
                option.click()
                return

        raise AssertionError(f"Опция '{option_text}' не найдена в списке")

    # локаторы
    afu_input = (By.CSS_SELECTOR, "app-file-uploader input[type='file'][name='files[]']")
    afu_upload_btn = (By.CSS_SELECTOR, "angular-file-uploader .afu-upload-btn")

    def upload_file(self, file_path: str, wait_seconds: int = 3) -> str:
        """Универсальная загрузка файла в hidden input (без проверки расширений на бэке)."""
        file_name = os.path.basename(file_path)

        # ждём инпут и загружаем файл
        afu_input_elem = self.wait_until_present(self.afu_input, timeout=2)
        afu_input_elem.send_keys(file_path)

        return file_name
    