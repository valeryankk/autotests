from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains    
from selenium.webdriver.common.keys import Keys
import random
import string
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException

class BasePage:
    error_locator = (By.CSS_SELECTOR, ".ui.icon.message.error")
    ERROR_CLOSE_BUTTON = (By.CSS_SELECTOR, "div.ui.icon.message.error i.close.icon")
    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.wait_long = WebDriverWait(driver, 60)

    def open(self, url):
        self.driver.get(url)

    def find(self, locator):
        return self.driver.find_element(*locator)
    
    def click(self, locator):
        self.wait_until_clickable(locator).click()
    
    def click_extra(self, locator):
        element = self.wait_until_visible(locator)
        print(element)
        #self.driver.execute_script("arguments[0].style.backgroundColor = 'red';", element)# для проверки к какой кнопке он обращается
        
        try:
            self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except ElementClickInterceptedException:
            print("Warning: элемент перекрыт, используем JS-клик")
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator, text):
        element = self.wait_until_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.wait_until_visible(locator).text

    def get_input_value(self, locator):
        return self.wait_until_visible(locator).get_attribute("value")
    
    def get_cell_value(self, locator: tuple) -> str:
        """
        Возвращает текст ячейки ag-Grid (gridcell).
        Берём сначала title, если он есть, иначе innerText.
        """
        element = self.wait_until_visible(locator)
        value = element.get_attribute("title")
        if value:
            return value.strip()
        return element.text.strip()

    
    def wait_until_input_value_is(self, locator, expected_value):
        self.wait.until(lambda d: d.find_element(*locator).get_attribute("value") == expected_value)

    def wait_until_present(self, locator, timeout=10):
        """
        Ожидает, что элемент появится в DOM (не обязательно будет виден).
        :param locator: tuple(By, "selector")
        :param timeout: время ожидания в секундах
        :return: WebElement
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Элемент {locator} не появился в DOM за {timeout} секунд"
        )
    def wait_until_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    def wait_until_visible_short(self, locator):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))

    def wait_until_visible_all(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def wait_until_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def is_element_displayed(self, locator):
        try:
            return self.find(locator).is_displayed()
        except:
            return False

    def set_text_input(self, locator, text: str):
        field = self.wait_until_visible(locator)
        field.clear()
        field.send_keys(text)

    def is_checkbox_selected(self, locator):
        checkbox = self.wait_until_visible(locator)
        return checkbox.is_selected()
    
    def get_attribute(self, locator, attribute_name, wait_visible=True):
        if wait_visible:
            element = self.wait_until_visible(locator)
        else:
            element = self.driver.find_element(*locator)
        return element.get_attribute(attribute_name)

    def get_text(self, locator):
        elem = self.wait_until_visible(locator)
        return elem.text

    def is_element_enabled(self, locator):
        elem = self.wait_until_visible(locator)
        return elem.is_enabled()
    
    def is_element_disabled(self, locator):
        elem = self.wait_until_visible(locator)
        return elem.get_attribute("disabled") is not None
    
    def wait_until_button_disabled(self, locator):
        self.wait.until(lambda driver: driver.find_element(*locator).get_attribute("disabled") is not None)

    def clear_field(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()

    def wait_long_until_element_disappears(self, locator):
        self.wait_long.until_not(EC.visibility_of_element_located(locator))

    def wait_until_element_disappears(self, locator):
        self.wait.until_not(EC.visibility_of_element_located(locator))

    @staticmethod
    def generate_random_name(prefix="Автотест", length=6):
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        name = prefix + " " + random_part
        return name
    
    @staticmethod
    def wait_until_rows_appear_or_timeout(driver, row_locator: tuple, timeout: int = 5) -> bool:
        """
        Ждёт, пока в таблице появятся строки с текстом или пока станет ясно, что таблица пуста.
        Возвращает True, если строки есть, False — если таблица пустая.
        """
        def _condition(d):
            rows = d.find_elements(*row_locator)
            if not rows:
                # ни одной строки — возможно, таблица пустая
                return False
            # строки есть — проверим, есть ли у них текст
            if any(el.text.strip() for el in rows):
                return True
            return None  # продолжаем ждать

        try:
            return WebDriverWait(driver, timeout).until(
                lambda d: _condition(d) is not None
            )
        except Exception:
            return False  # таймаут без данных — считаем пустой
        
    def click_element_with_hover(self, hover_locator, click_locator):
        """
        Наводится на элемент hover_locator, затем кликает по элементу click_locator.
        Используется для элементов, которые появляются только при наведении.
        """
        hover_element = self.wait_until_visible(hover_locator)
        actions = ActionChains(self.driver)
        actions.move_to_element(hover_element).perform()  # Навести курсор

        click_element = self.wait_until_visible(click_locator)
        actions.move_to_element(click_element).click().perform()



    def remove_and_fill(self, locator, value):
        """Очищает и заполняет поле с помощью ActionChains."""
        field = self.wait_until_visible(locator)

        # Явный клик, чтобы элемент получил фокус
        field.click()

        actions = ActionChains(self.driver)
        actions.move_to_element(field).click().pause(0.2)
        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).pause(0.2)
        actions.send_keys(Keys.BACKSPACE).pause(0.2)
        actions.send_keys(value).pause(0.2).send_keys(Keys.ENTER)
        actions.perform()

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
    
    def get_truncated_input_value(self, locator, attempt_value: str, expected_max: float) -> float:
        """
        Вводит attempt_value в поле и возвращает реальное значение,
        которое отобразилось после валидации (например, обрезанное).
        Если attempt_value > expected_max → поле 'обрезает' ввод на предпоследней цифре.
        """
        self.remove_and_fill(locator, attempt_value)
        self.lose_focus_by_click()
        raw_val = self.get_input_value(locator).replace(",", ".").strip()

        # Если ничего не ввелось → считаем 0
        if not raw_val:
            return 0.0

        try:
            return float(raw_val)
        except ValueError:
            raise AssertionError(f"Невозможно преобразовать '{raw_val}' в число после ввода {attempt_value}")

    def lose_focus_by_click(self):
        """Теряет фокус кликом по другому месту"""
        # Кликаем по body или другому нейтральному элементу
        body = self.find((By.TAG_NAME, "body"))
        body.click()
        print("Фокус сброшен кликом по body")


    def validate_fraction_or_trimmed(self, locator, attempt_value: str, expected_max: float, precision: int = 6) -> float:
        """
        Вводит attempt_value и проверяет:
        - что дробная часть числа не превышает precision знаков
        - либо дробная часть полностью сбросилась (отрезались нули)
        
        Возвращает реальное число (float), отображённое в поле.
        """
        self.remove_and_fill(locator, attempt_value)
        raw_val = self.get_input_value(locator).replace(",", ".").strip()

        if not raw_val:
            return 0.0

        # Проверка дробной части
        if "." in raw_val:
            fraction = raw_val.split(".")[-1]
            assert len(fraction) <= precision, \
                f"Дробная часть '{fraction}' слишком длинная (>{precision}) после ввода {attempt_value}"
        else:
            # дробная часть отброшена → допускается только целое число
            assert raw_val.isdigit(), \
                f"После отброса дробной части ожидали целое число, получили '{raw_val}'"

        try:
            value = float(raw_val)
        except ValueError:
            raise AssertionError(f"Невозможно преобразовать '{raw_val}' в число")

        # Проверка попадания в диапазон (универсально для всех полей)
        assert value <= expected_max, \
            f"Число {value} превысило верхнюю границу {expected_max} (после ввода {attempt_value})"

        return value
    def edit_grid_cell(self, locator, value: str): # работает только при первичном вводе
        """
        Редактирует ячейку ag-Grid (div[role='gridcell']).
        Логика: клик -> поле становится редактируемым -> ввод значения -> Enter.
        """
        cell = self.wait_until_visible(locator)

        # Клик по ячейке для активации редактирования
        cell.click()

        # Иногда ag-grid не сразу переводит div в режим input → пробуем Enter
        try:
            actions = ActionChains(self.driver)
            actions.double_click(cell).perform()  # двойной клик почти всегда открывает редактор
        except Exception:
            pass

        # Теперь ищем editable input (он появляется внутри ячейки)
        try:
            input_el = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ag-cell input"))
            )
            input_el.clear()
            input_el.send_keys(value)
            input_el.send_keys(Keys.ENTER)
        except Exception:
            raise AssertionError(f"Не удалось ввести значение '{value}' в ячейку {locator}")

    def edit_grid_cell_via_keys(self, locator, value: str):
        """
        Вводит значение в ag-Grid ячейку через F2 (режим редактирования) + send_keys.
        Полезно, если input не появляется или Selenium не ловит его напрямую.
        """
        cell = self.wait_until_visible(locator)

        # Клик по ячейке
        cell.click()

        actions = ActionChains(self.driver)
        actions.click(cell).send_keys(Keys.F2).perform()  # активируем режим редактирования

        # Вводим значение посимвольно
        actions = ActionChains(self.driver)
        actions.send_keys(value).send_keys(Keys.ENTER).perform()

        # Проверяем, что значение применилось
        raw_value = cell.text.strip().replace(",", ".")
        if str(value) not in raw_value:
            raise AssertionError(f"Ожидалось '{value}', но в ячейке отображается '{raw_value}'")
        
    
    def close_error_notification(self,alert):
        """Закрывает уведомление об ошибке кликом на крестик"""
        if self.is_element_displayed(self.ERROR_CLOSE_BUTTON):
            self.click(self.ERROR_CLOSE_BUTTON)
            self.wait_until_element_disappears(alert)

    def close_all_modals_if_present(self):
        """
        Проверяет наличие модальных окон и нажимает кнопку 'Отмена' в них.
        Если кнопки 'Отмена' нет, пытается закрыть крестиком или другим способом.
        """
        try:
            # Ищем все видимые модальные окна
            modals = self.driver.find_elements(By.CSS_SELECTOR, "modal-container")
            
            for modal in modals:
                try:
                    # Пробуем найти кнопку "Отмена"
                    cancel_buttons = modal.find_elements(By.XPATH, ".//button[contains(text(), 'Отмена')]")
                    
                    if cancel_buttons:
                        # Кликаем первую найденную кнопку "Отмена"
                        self.driver.execute_script("arguments[0].click();", cancel_buttons[0])
                        print("Найдено и закрыто модальное окно кнопкой 'Отмена'")
                    else:
                        # Если нет кнопки "Отмена", пробуем крестик
                        close_buttons = modal.find_elements(By.CSS_SELECTOR, "button.close, button[aria-label='Close']")
                        if close_buttons:
                            self.driver.execute_script("arguments[0].click();", close_buttons[0])
                            print("Найдено и закрыто модальное окно крестиком")
                        else:
                            # Если ничего не найдено, пробуем клик по затемненной области
                            backdrop = self.driver.find_elements(By.CSS_SELECTOR, "div.modal-backdrop.fade.show")
                            if backdrop:
                                self.driver.execute_script("arguments[0].click();", backdrop[0])
                                print("Найдено и закрыто модальное окно кликом по backdrop")
                            
                except Exception as modal_error:
                    print(f"Ошибка при закрытии модального окна: {modal_error}")
                    continue
                    
            # Ждем исчезновения модальных окон
            self.wait_until_element_disappears((By.CSS_SELECTOR, "modal-container"))
            
        except Exception as e:
            print(f"Ошибка при проверке модальных окон: {e}")

    def wait_until_no_modals(self, timeout=5):
        """
        Ждет, пока все модальные окна исчезнут
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "modal-container.modal.fade.show"))
            )
        except:
            # Если таймаут, продолжаем выполнение
            pass

    def wait_until_checkbox_checked(self, wrapper_element, timeout=10):
        """
        Ожидает, пока чекбокс станет отмеченным (появится класс ag-checked).
        """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: "ag-checked" in wrapper_element.get_attribute("class"),
            message=f"Чекбокс не стал отмеченным в течение {timeout} секунд"
        )

    def wait_until_checkbox_unchecked(self, wrapper_element, timeout=10):
        """
        Ожидает, пока чекбокс станет неотмеченным (исчезнет класс ag-checked).
        """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: "ag-checked" not in wrapper_element.get_attribute("class"),
            message=f"Чекбокс не снял отметку в течение {timeout} секунд"
        )

    def wait_for_particular_text_in_field(self, locator, expected_text: str, timeout: int = 10) -> bool: #пока не проверяла - на будущее
        """
        Ждёт появления expected_text в поле (input/div/textarea).
        Возвращает True, если текст появился, иначе бросает AssertionError.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: expected_text in d.find_element(*locator).text
                        or expected_text in d.find_element(*locator).get_attribute("value")
            )
            return True
        except TimeoutException:
            raise AssertionError(
                f"Текст '{expected_text}' не появился в поле {locator} в течение {timeout} секунд"
            )


    def wait_for_field_not_empty(self, locator, timeout: int = 10) -> bool:
        """
        Ждёт, пока поле (input/textarea/div) перестанет быть пустым.
        Смотрит и на .text, и на value (для input).
        Возвращает True, если поле стало непустым, иначе AssertionError.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: (
                    (text := d.find_element(*locator).text.strip()) != "" or
                    (value := d.find_element(*locator).get_attribute("value") or "").strip() != ""
                )
            )
            return True
        except TimeoutException:
            raise AssertionError(
                f"Поле {locator} осталось пустым в течение {timeout} секунд"
            )