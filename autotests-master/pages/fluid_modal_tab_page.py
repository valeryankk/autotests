#Page Object для ВКЛАДКИ модели флюида
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from pages.create_fluid_model_modal import CreateFluidModelModal
from selenium.webdriver.common.action_chains import ActionChains  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
class FluidModelTab(BasePage):

    #вкладки на пг
    fluid_model_tab = (By.XPATH, "//a[contains(text(), 'МОДЕЛИ ФЛЮИДА')]")
    plast_model_tab = (By.XPATH, "//a[contains(text(), 'МОДЕЛИ ПЛАСТА')]")
    plast_model_tab_mathbalance = (By.XPATH, "//a[contains(text(), 'Матбаланс')]")
    plast_model_tab_polinom = (By.XPATH, "//a[contains(text(), 'Полином')]")
    wells_tab = (By.XPATH, "//a[contains(text(), 'СКВАЖИНЫ')]")
    network_tab = (By.XPATH, "//a[contains(text(), 'СЕТЬ СБОРА')]")
    event_tab = (By.XPATH, "//a[contains(text(), 'СОБЫТИЯ')]")
    products_tab = (By.XPATH, "//a[contains(text(), 'ПРОДУКЦИЯ')]")
    zonal_model = (By.XPATH, "//a[contains(text(), 'ЗОННАЯ МОДЕЛЬ')]")

    # Локаторы строк таблиц на вкладках
    fluid_model_rows = (By.CSS_SELECTOR, '#fluidModelGrid [role="row"]')
    plast_model_rows = (By.CSS_SELECTOR, '#layerModelZoneGrid [role="row"]') #матбаланс
    plast_model_rows_polynom = (By.CSS_SELECTOR, '#layerModelPolynomialGrid [role="row"]')#полином
    wells_rows = (By.CSS_SELECTOR, '#fluidModelGrid [role="row"]') # id повторяертся - проверить как работает.
    event_rows = (By.CSS_SELECTOR, '#naturalGasEventsGrid [role="row"]')
    products_rows = (By.CSS_SELECTOR, '#colNetProductGrid [role="row"]')

    fluid_model_header = ["псевдокритическое давление газа", "псевдокритическая температура газа"]
    plast_model_header_mathbalance = ["начальное пластовое давление", "запасы газа" ]
    plast_model_header_polinom = ["пластовая температура", "накопленная добыча газа"]
    wells_header = ["месторождение", "лицензионный участок"]

    name_fluid_header = (By.XPATH, '//*[@id="fluidModelGrid"]//div[contains(@class,"header__label") and text()="Наименование"]')
    locator_sort_order_span = (By.XPATH, '//*[@id="fluidModelGrid"]//div[contains(@class,"header")]//span[contains(@class,"header__sort-order")]')


    # Локатор для контейнера сети сбора
    collection_network_container = (By.CSS_SELECTOR, "app-collection-network")
    # Локатор для кнопки создания внутри контейнера
    create_button = (By.XPATH, "//button[@class='btn btn-secondary mx-1' and normalize-space()='Создать']")
    edit_button = (By.XPATH, "//button[contains(@class, 'btn-secondary') and contains(text(), 'Редактировать')]")
    delete_button =(By.XPATH, "//button[contains(@class, 'btn-secondary') and contains(text(), 'Удалить')]")
    results_button = (By.XPATH, "//button[contains(@class, 'btn-secondary') and contains(text(), 'Результаты расчета')]")

    # Локатор для ссылок сетей (теги <a>) внутри контейнера
    network_links = (By.CSS_SELECTOR, "app-collection-network a")

    any_modal = (By.CSS_SELECTOR, "modal-container")

    # Контейнер с таблицей (строки флюидов)
    table_body = (By.CSS_SELECTOR, "div.ag-body-viewport.ag-layout-normal.ag-row-no-animation") 
    row_checkboxes = (By.CSS_SELECTOR, "div.ag-row input.ag-checkbox-input") # колонка чекбокс
    rows = (By.CSS_SELECTOR, "div.ag-row")
    row_checkbox = (By.CSS_SELECTOR, "input.ag-checkbox-input")


    # Контейнер таблицы флюидов
    fluid_grid_container = (By.CSS_SELECTOR, "div.ag-center-cols-container")

    # Строки таблицы флюидов (уникальные колонки)
    FLUID_MODEL_ROWS = (By.CSS_SELECTOR, "div[col-id='name'], div[col-id='pseudoCriticalGasPressure'], div[col-id='pseudoCriticalGasTemperature']")

    

    def is_fluid_model_list_not_empty(self) -> bool: 
        """Проверяет, что список моделей флюида не пустой (хотя бы одна строка с данными)."""
        self.wait_until_visible((By.ID, "fluidModelGrid"))  # Убедиться, что таблица загружена

        # Не ждём, просто пробуем найти строки (может быть 0 штук)
        rows = self.driver.find_elements(*self.fluid_model_rows)
        for row in rows:
            try:
                name_cell = row.find_element(By.CSS_SELECTOR, "div[row-index] div[col-id='name']")
                if name_cell.text.strip():
                    return True
            except Exception:
                continue

        return False
    
    def get_model_rows_as_lists(self, grid_id: str, row_locator: tuple, header_keywords: list[str], max_rows: int = 3):
        self.wait_until_visible((By.ID, grid_id))

        result = []
        row_index = 0

        while len(result) < max_rows:
            try:
                # Находим все строки *каждый раз заново*
                rows = self.driver.find_elements(*row_locator)
                if row_index >= len(rows):
                    break

                row = rows[row_index]
                text = row.text.strip()

                if not text:
                    row_index += 1
                    continue

                if any(keyword.lower() in text.lower() for keyword in header_keywords):
                    row_index += 1
                    continue

                row_data = [cell.strip() for cell in text.split('\n') if cell.strip()]
                result.append(row_data)
                row_index += 1

            except StaleElementReferenceException:
                # Если элемент исчез — пробуем снова с тем же индексом
                continue

        return result
    
    def get_table_headers(self) -> list[str]:
        headers = self.driver.find_elements(
            By.XPATH, '//*[@id="fluidModelGrid"]//div[contains(@class, "header__label")]'
        )
        return [h.text.strip() for h in headers if h.text.strip()]

    def is_editing_disabled(self) -> bool:
        """Проверяет, что ячейки таблицы не редактируемые"""
        rows = self.driver.find_elements(*self.fluid_model_rows)
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "div.ag-cell")
            for cell in cells:
                if "editable" in cell.get_attribute("class"):
                    return False
        return True

    def get_unit_dropdowns(self):
        """Возвращает список дропдаунов единиц измерения"""
        return self.driver.find_elements(*self.unit_dropdowns)

    def click_create_button(self):
        """Нажимает кнопку 'Создать'"""
        btn = self.wait_until_clickable(self.fluid_create_button)
        btn.click()

    def open_fluid_model_tab(self):
        """Открывает вкладку 'МОДЕЛИ ФЛЮИДА'."""
        tab = self.wait_until_clickable(self.fluid_model_tab)
        tab.click()
        self.wait_until_visible((By.ID, "fluidModelGrid"))

    def is_column_present(self, column_name: str) -> bool:
        """
        Проверяет наличие колонки по имени в таблице 'Зонная модель'.
        """
        header_locator = (
            By.XPATH,
            f'//*[@id="fluidModelGrid"]//div[contains(@class,"header__label") and normalize-space(text())="{column_name}"]'
        )
        try:
            self.wait_until_visible(header_locator, timeout=2)
            return True
        except Exception:
            return False
        
    # Локатор для всех ячеек с именами флюидов
    fluid_names_cells = (By.CSS_SELECTOR, "div.ag-cell[col-id='name']")
    '''
    def is_fluid_present(self, name: str) -> bool:
        """
        Проверяет, есть ли в реестре флюид с указанным именем.
        """
        elements = self.driver.find_elements(*self.fluid_names_cells)
        return any(name.strip() == el.text.strip() for el in elements)'''
    
    def wait_for_fluid_present(self, grid_css: str, name: str, timeout: int = 8) -> bool:
        """
        Ждёт, пока флюид с именем `name` появится в реестре (в колонке col-id='name').
        Метод простой: использует self.is_fluid_present(grid_css, name) внутри WebDriverWait.
        По успеху возвращает True. По таймауту бросает AssertionError.
        """
        try:
            WebDriverWait(self.driver, timeout).until(lambda _: self.is_fluid_present(grid_css, name))
            return True
        except TimeoutException:
            raise AssertionError(f"Флюид с именем '{name}' не появился в реестре (grid={grid_css}) в течение {timeout} секунды(д).")


    def is_fluid_present(self, grid_css: str, name: str) -> bool:
        """
        Быстрая проверка: есть ли в колонке col-id='name' ячейка с точным текстом name.
        Возвращает True/False без ожиданий.
        """
        try:
            # Ищем все ячейки колонки name в данном grid (CSS-локатор)
            cells = self.driver.find_elements(By.CSS_SELECTOR, f"{grid_css} div[col-id='name']")
            for c in cells:
                try:
                    if (c.text or "").strip() == name:
                        return True
                except StaleElementReferenceException:
                    # элемент устарел — пропускаем (проверим другие)
                    continue
            return False
        except Exception:
            return False
    
    def get_all_fluids_by_name(self, name: str):
        """
        Возвращает список элементов, соответствующих флюидам с заданным именем.
        """
        elements = self.driver.find_elements(*self.fluid_names_cells)
        return [el for el in elements if name.strip() == el.text.strip()]
    

    def unselect_all_rows(self):
        """
        Снимает все отметки в таблице флюидов.
        """
        try:
            # Ищем все обертки чекбоксов с классом ag-checked (выделенные)
            checked_wrappers = self.driver.find_elements(
                By.CSS_SELECTOR, "div.ag-wrapper.ag-input-wrapper.ag-checkbox-input-wrapper.ag-checked"
            )
            
            for wrapper in checked_wrappers:
                try:
                    # Находим ячейку чекбокса (родительский элемент) и кликаем по ней
                    checkbox_cell = wrapper.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ag-cell')]")
                    checkbox_cell.click()
                    
                    # Ждем снятия отметки
                    self.wait.until(
                        lambda driver: "ag-checked" not in wrapper.get_attribute("class")
                    )
                    
                except Exception as e:
                    print(f"Не удалось кликнуть по ячейке чекбокса: {e}")
                    continue
                    
        except Exception as e:
            print(f"Не удалось найти выделенные чекбоксы: {e}")  




    def select_row_by_index(self, index: int):
        """
        Выбирает строку в таблице по индексу (начиная с 1).
        """
        try:
            # Способ 2: клик по ячейке с чекбоксом
            cell_locator = (By.CSS_SELECTOR, f"div.ag-row[row-index='{index-1}'] div[col-id='checkbox']")
            cell = self.wait_until_visible(cell_locator)
            
            # Находим обертку чекбокса для проверки состояния
            wrapper = cell.find_element(By.CSS_SELECTOR, "div.ag-checkbox-input-wrapper")
            
            # Кликаем только если не отмечено
            if "ag-checked" not in wrapper.get_attribute("class"):
                cell.click()
                # Ждем отметки (используем WebDriverWait напрямую)
                self.wait.until(
                    lambda driver: "ag-checked" in wrapper.get_attribute("class")
                )
                
        except Exception as e:
            raise AssertionError(f"Не удалось выбрать строку {index}: {e}")
        
    def sort_header_locator(self, grid_css: str, col_id: str):
        return (By.CSS_SELECTOR, f"{grid_css} div[col-id='{col_id}'] .header__label")

    def sort_order_indicator_locator(self, grid_css: str, col_id: str):
        return (By.CSS_SELECTOR, f"{grid_css} div[col-id='{col_id}'] .header__sort-order")

    def sort_up_icon_locator(self, grid_css: str, col_id: str):
        return (By.CSS_SELECTOR, f"{grid_css} div[col-id='{col_id}'] .header__sort-up-label")

    def sort_down_icon_locator(self, grid_css: str, col_id: str):
        return (By.CSS_SELECTOR, f"{grid_css} div[col-id='{col_id}'] .header__sort-down-label")


    def reset_sorting(self, col_id="name", grid_css="#fluidModelGrid"):
        """
        Сбрасывает сортировку до исходного состояния для колонки col_id в таблице grid_css.
        """
        sort_header = self.sort_header_locator(grid_css, col_id)
        sort_order_indicator = self.sort_order_indicator_locator(grid_css, col_id)
        sort_up_icon = self.sort_up_icon_locator(grid_css, col_id)
        sort_down_icon = self.sort_down_icon_locator(grid_css, col_id)

        header = self.wait_until_clickable(sort_header)

        try:
            sort_order = self.driver.find_element(*sort_order_indicator)
            current_order = (sort_order.get_attribute("textContent") or "").strip()
            if "0" in current_order:
                return
        except Exception:
            return

        if self.is_element_displayed(sort_up_icon):
            clicks_needed = 2
        elif self.is_element_displayed(sort_down_icon):
            clicks_needed = 1
        else:
            clicks_needed = 2

        for _ in range(clicks_needed):
            header.click()
            #time.sleep(0.5)
            try:
                current_order = (self.driver.find_element(*sort_order_indicator).get_attribute("textContent") or "")
                if "0" in current_order:
                    break
            except Exception:
                break


    def get_sorted_row_data(self, col_ids=None, max_rows=6, grid_css="#fluidModelGrid"):
        """
        Получает данные строк таблицы grid_css, используя text элемента.
        Возвращает list[list] — строки × колонки.
        """
        self.wait_until_visible((By.CSS_SELECTOR, grid_css))

        if col_ids is None:
            col_ids = ['name', 'pseudoCriticalGasPressure', 'pseudoCriticalGasTemperature', 'relativeDensity']

        row_data = []

        for row_index in range(2, 2 + max_rows):
            try:
                row = self.driver.find_element(
                    By.CSS_SELECTOR, f"{grid_css} div.ag-row[aria-rowindex='{row_index}']"
                )
            except Exception:
                break

            row_values = []
            for col_id in col_ids:
                try:
                    cell = row.find_element(By.CSS_SELECTOR, f"div[col-id='{col_id}']")
                    row_values.append(cell.text)
                except Exception as e:
                    print(f"Ошибка получения ячейки {col_id}: {e}")
                    row_values.append("")
            if any(val.strip() for val in row_values):
                row_data.append(row_values)

        return row_data


    def get_name_column_values(self, max_rows=6, col_id="name", grid_css="#fluidModelGrid"):
        """
        Получает значения колонки col_id (по умолчанию 'name') в таблице grid_css.
        """
        self.wait_until_visible((By.CSS_SELECTOR, grid_css))

        values = []
        for row_index in range(2, 2 + max_rows):
            try:
                cell = self.driver.find_element(
                    By.CSS_SELECTOR, f"{grid_css} div.ag-row[aria-rowindex='{row_index}'] div[col-id='{col_id}']"
                )
                if cell.text.strip():
                    values.append(cell.text)
            except Exception:
                break

        print(f"Значения {col_id}: {values}")
        return values
    




    # -----------------------------------------
    # Методы для фильтров реестра флюидов
    # -----------------------------------------

    def sort_header_locator(self, grid_css: str, col_id: str):
        """Локатор для текстового лейбла хедера (по которому был прежний click)."""
        return (By.CSS_SELECTOR, f"{grid_css} div[col-id='{col_id}'] .header__label")

    def header_cell_locator(self, grid_css: str, col_id: str):
        """Локатор для контейнера хедера (в нём появляется класс ag-column-menu-visible)."""
        return (By.CSS_SELECTOR, f"{grid_css} div.ag-header-cell[col-id='{col_id}']")
    
