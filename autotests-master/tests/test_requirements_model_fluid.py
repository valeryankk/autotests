import pytest
from selenium.webdriver.common.by import By
from pages.create_fluid_model_modal import CreateFluidModelModal
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


# +1. Вложенная вкладка "Зонная модель" содержит таблицу с перечнем созданных флюидов
def test_fluid_model_tab_has_fluid_table(created_json_version, fluid_model_page,forecast_registry_page):
    fluid_model_page.open_fluid_model_tab()
    assert fluid_model_page.is_fluid_model_list_not_empty(), \
        "Таблица моделей флюида пуста, но должна содержать данные из JSON"

# +В таблице 'Зонная модель' присутствуют ожидаемые колонки
def test_fluid_model_table_columns_have_correct_headers(created_json_version, fluid_model_page):
    fluid_model_page.open_fluid_model_tab()

    expected_columns = ["Наименование", "Псевдокритическое давление газа", "Псевдокритическая температура газа"]

    actual_headers = fluid_model_page.get_table_headers()
    for expected_column in expected_columns:
        assert any(expected_column.lower() in header.lower() for header in actual_headers), \
            f"Колонка '{expected_column}' не найдена в заголовках таблицы. Actual: {actual_headers}"

# +8. В таблице присутствует колонка 'Отметка'. Проверяем наличие хедера колонки с col-id='checkbox' в НЕ пустом реестрe
def test_fluid_registry_has_mark_column_header(created_json_version, fluid_model_page):
    header_checkbox = fluid_model_page.driver.find_elements(
        By.CSS_SELECTOR,
        "div.ag-header-cell[col-id='checkbox']"
    )
    assert len(header_checkbox) > 0, "В таблице отсутствует колонка 'Отметка' (col-id='checkbox')"

# +Проверяем, что в строках таблицы есть ячейки - чекбоксы для отметки.
def test_fluid_registry_has_mark_column_cells(created_json_version, fluid_model_page):
    row_checkboxes = fluid_model_page.driver.find_elements(
        By.CSS_SELECTOR,
        "div.ag-cell[col-id='checkbox'] input[type='checkbox']"
    )
    assert len(row_checkboxes) > 0, "В таблице отсутствуют чекбоксы в строках колонки 'Отметка'"


# +14. Кнопка 'Редактировать' активна при единичной отметке в таблице флюидов. После нажатия открывается форма редактирования флюида.
def test_edit_button_active_with_single_selection(created_json_version, fluid_model_page, filled_form):

    # 1. Убеждаемся, что список флюидов не пустой
    fluids = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.fluid_model_rows,
        header_keywords= fluid_model_page.fluid_model_header)

    fluid_model_page.wait_until_visible(fluid_model_page.table_body)
    assert len(fluids) > 0, "В реестре нет флюидов для теста"

    # 2. Снимаем выделение со всех строк (если есть)
    fluid_model_page.unselect_all_rows()

    # 3. Отмечаем одну строку
    fluid_model_page.select_row_by_index(1)

    # 4. Проверяем, что кнопка "Редактировать" активна
    edit_button = fluid_model_page.wait_until_visible(fluid_model_page.edit_button)
    fluid_model_page.wait_until_clickable(fluid_model_page.edit_button)
    assert edit_button.is_enabled(), "Кнопка 'Редактировать' должна быть активна при выделении 1 строки"

    # 5. Кликаем "Редактировать"
    fluid_model_page.click_extra(fluid_model_page.edit_button)

    # 6. Проверяем, что открылось модальное окно редактирования флюида
    modal = CreateFluidModelModal(filled_form.driver)
    modal.wait_until_visible(modal.modal)
    assert modal.is_element_displayed(modal.name_field), "Форма редактирования флюида не открылась"


# +14  Проверяет, что при выборе нескольких флюидов кнопка Редактировать неактивна.

def test_multiple_selection_disables_edit_button(created_json_version, fluid_model_page):
    # Подготовка данных - убедимся, что есть хотя бы 2 флюида
    fluids = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.fluid_model_rows,
        header_keywords=fluid_model_page.fluid_model_header
    )
    fluid_model_page.wait_until_visible(fluid_model_page.table_body)
    assert len(fluids) >= 2, "Нужно минимум 2 флюида для теста"

    # Сбрасываем выделение
    fluid_model_page.unselect_all_rows()
    fluid_model_page.wait_until_button_disabled(fluid_model_page.edit_button)
    assert fluid_model_page.is_element_disabled(fluid_model_page.edit_button), "Кнопка 'Редактировать' должна быть неактивна при отсутствии выбора"

    # Выбираем первый флюид
    fluid_model_page.select_row_by_index(1)

    # Выбираем второй флюид (множественный выбор)
    fluid_model_page.select_row_by_index(2)
    fluid_model_page.wait_until_button_disabled(fluid_model_page.edit_button)
    # Проверяем, что кнопка неактивна
    assert fluid_model_page.is_element_disabled(fluid_model_page.edit_button), "Кнопка 'Редактировать' должна быть неактивна при множественном выборе"


# 15. +Кнопка 'Удалить' активна при единичной или множественной отметке в таблице флюидов. После нажатия открывается окно подтверждения.
def test_delete_button_active_with_selection(created_json_version, fluid_model_page):

    # 1. Убеждаемся, что список флюидов не пустой
    fluids = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.fluid_model_rows,
        header_keywords=fluid_model_page.fluid_model_header
    )
    fluid_model_page.wait_until_visible(fluid_model_page.table_body)
    assert len(fluids) >= 2, "Для теста нужно как минимум 2 флюида в реестре"

    # 2. Снимаем выделение со всех строк
    fluid_model_page.unselect_all_rows()
    fluid_model_page.wait_until_button_disabled(fluid_model_page.delete_button)
    assert fluid_model_page.is_element_disabled(fluid_model_page.delete_button), "Кнопка 'Удалить' должна быть неактивна при отсутствии выбора"

    # 4. Отмечаем первую строку (единичный выбор)
    fluid_model_page.select_row_by_index(1)
    fluid_model_page.wait_until_clickable(fluid_model_page.delete_button)
    assert fluid_model_page.is_element_enabled(fluid_model_page.delete_button), "Кнопка 'Удалить' должна быть активна при единичном выборе"

    # 5. Отмечаем вторую строку (множественный выбор)
    fluid_model_page.select_row_by_index(2)
    fluid_model_page.wait_until_clickable(fluid_model_page.delete_button)
    assert fluid_model_page.is_element_enabled(fluid_model_page.delete_button), "Кнопка 'Удалить' должна быть активна при множественном выборе"

    # 6. Нажимаем кнопку удаления и проверяем окно подтверждения
    fluid_model_page.click_extra(fluid_model_page.delete_button)

    # Проверяем, что открылось окно подтверждения
    fluid_model_page.wait_until_visible(fluid_model_page.any_modal)
    assert fluid_model_page.is_element_displayed(fluid_model_page.any_modal), "Должно открыться окно подтверждения удаления"

    # 7. Закрываем окно подтверждения (отмена удаления)
    fluid_model_page.close_all_modals_if_present()


# +17. После нажатия кнопки "Создать" открывается модальное окно, заблокировав другие элементы на темном фоне.
def test_create_button_opens_modal_with_overlay(created_json_version, fluid_model_page):

    # 1. Нажимаем кнопку "Создать"
    fluid_model_page.click(fluid_model_page.create_button)

    # 2. Проверяем, что открылось модальное окно
    fluid_model_page.wait_until_visible(fluid_model_page.any_modal)
    assert fluid_model_page.is_element_displayed(fluid_model_page.any_modal), "Должно открыться модальное окно"

    # 3. Проверяем, что модальное окно блокирует взаимодействие с другими элементами
    # Проверяем, что элементы под модалом не кликабельны через попытку клика
    try:
        fluid_model_page.click(fluid_model_page.create_button)
        modal_blocks = False
    except:
        modal_blocks = True

    assert modal_blocks, "Модальное окно должно блокировать взаимодействие с другими элементами"

    fluid_model_page.close_all_modals_if_present()

#   +16. Кнопка "Результаты расчета" активна всегда. После нажатия открывается окно результатов расчета.
def test_calculation_results_button_always_active(created_json_version, fluid_model_page):

    # 1. Проверяем, что кнопка активна без выделения
    fluid_model_page.unselect_all_rows()
    fluid_model_page.wait_until_clickable(fluid_model_page.results_button)
    assert fluid_model_page.is_element_enabled(fluid_model_page.results_button), "Кнопка 'Результаты расчета' должна быть активна без выбора"

    # 2. Проверяем, что кнопка активна при единичном выделении
    fluid_model_page.select_row_by_index(1)
    fluid_model_page.wait_until_clickable(fluid_model_page.results_button)
    assert fluid_model_page.is_element_enabled(fluid_model_page.results_button), "Кнопка 'Результаты расчета' должна быть активна при единичном выборе"

    # 3. Проверяем, что кнопка активна при множественном выделении
    fluid_model_page.select_row_by_index(2)
    fluid_model_page.wait_until_clickable(fluid_model_page.results_button)
    assert fluid_model_page.is_element_enabled(fluid_model_page.results_button), "Кнопка 'Результаты расчета' должна быть активна при множественном выборе"

    # 4. Нажимаем кнопку и проверяем открытие окна результатов
    fluid_model_page.click(fluid_model_page.results_button)

    main_window = fluid_model_page.driver.current_window_handle
    # Ждем и переключаемся на новое окно
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: len(driver.window_handles) > 1
    )
    new_window = [w for w in fluid_model_page.driver.window_handles if w != main_window][0]
    fluid_model_page.driver.switch_to.window(new_window)

    # Проверяем новое окно
    assert "natural-gas-result" in fluid_model_page.driver.current_url.lower()

    # Закрываем новое окно и возвращаемся
    fluid_model_page.driver.close()
    fluid_model_page.driver.switch_to.window(main_window)  # ← ВОЗВРАТ В ГЛАВНОЕ ОКНО


#4 + Редактирование значений в таблице реестра флюидов запрещено
def test_table_cells_not_editable(created_json_version, fluid_model_page):
    # Ждем загрузки конкретно таблицы флюидов по ID
    fluid_model_page.wait_until_visible(fluid_model_page.fluid_grid_container)

    col_ids = [
    'pseudoCriticalGasPressure',
    'pseudoCriticalGasTemperature',
    'relativeDensity'
    ]

    cells = []
    for col_id in col_ids:
        elements = fluid_model_page.driver.find_elements(By.CSS_SELECTOR, f"div[col-id='{col_id}']")
        if elements:
            # Берем элемент с индексом 1 или 0, если только один элемент
            index = 1 if len(elements) > 1 else 0
            cells.append(elements[index])
    assert len(cells) > 0, "Не найдено ячеек с данными в таблице флюидов"

    for cell in cells:

        original_text = cell.text
        # проверяем с помощью send_keys
        try:
            original_text = cell.text
            cell.click()
            cell.send_keys("40")
            current_text = cell.text
            assert str(current_text) == str(original_text), 'текст в ячейке изменился'
        except ElementNotInteractableException:
            print('не редактируется')

        # Проверяем с двойным кликом
        cell.click()
        inputs_after_click = cell.find_elements(By.CSS_SELECTOR, "input")
        assert len(inputs_after_click) == 0, "Клик не должен активировать редактирование"

        actions = ActionChains(fluid_model_page.driver)
        actions.double_click(cell).perform()
        inputs_after_double_click = cell.find_elements(By.CSS_SELECTOR, "input")
        assert len(inputs_after_double_click) == 0, "Двойной клик не должен активировать редактирование"
        assert cell.text == original_text, "Текст ячейки не должен меняться"


def test_column_sorting_behavior_1(created_json_version, fluid_model_page):
    """
    Проверка поведения сортировки столбцов в таблице флюидов.
    Цикл: нет сортировки → прямая сортировка → обратная сортировка → нет сортировки.
    """
    # Локаторы для сортировки
    sort_header = (By.CSS_SELECTOR, "#fluidModelGrid div[col-id='name'] .header__label") #ячейка 'Наименование'
    sort_order_indicator = (By.CSS_SELECTOR, "#fluidModelGrid div[col-id='name'] .header__sort-order") #элемент, где хранится 0/1
    sort_up_icon= (By.CSS_SELECTOR, "#fluidModelGrid div[col-id='name'] .header__sort-up-label") # стрелка вверх (появляется после клика)
    sort_down_icon = (By.CSS_SELECTOR, "#fluidModelGrid div[col-id='name'] .header__sort-down-label") # стрелка вниз (появляется после клика)

    # 1. Исходное состояние - нет сортировки
    sort_order = fluid_model_page.driver.find_element(*sort_order_indicator)
    print('ПОКАЗАТЕЛЬ ', sort_order.get_attribute("textContent"))
    assert "0" in sort_order.get_attribute("textContent"), "Изначально не должно быть примененной сортировки"
    assert not fluid_model_page.is_element_displayed(sort_up_icon), "Иконка прямой сортировки не должна отображаться"
    assert not fluid_model_page.is_element_displayed(sort_down_icon), "Иконка обратной сортировки не должна отображаться"

    # 2. Первый клик - прямая сортировка (по возрастанию)
    header = fluid_model_page.wait_until_clickable(sort_header)
    header.click()

    # Проверяем прямую сортировку
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "1" in driver.find_element(*sort_order_indicator).get_attribute("textContent")
    )
    assert fluid_model_page.is_element_displayed(sort_up_icon), "Должна отображаться иконка прямой сортировки"
    assert not fluid_model_page.is_element_displayed(sort_down_icon), "Иконка обратной сортировки не должна отображаться"

    # 3. Второй клик - обратная сортировка (по убыванию)
    header.click()

    # Проверяем обратную сортировку
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "1" in driver.find_element(*sort_order_indicator).get_attribute("textContent")
    )
    assert not fluid_model_page.is_element_displayed(sort_up_icon), "Иконка прямой сортировки не должна отображаться"
    assert fluid_model_page.is_element_displayed(sort_down_icon), "Должна отображаться иконка обратной сортировки"

    # 4. Третий клик - сброс сортировки
    header.click()

    # Проверяем отсутствие сортировки
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "0" in driver.find_element(*sort_order_indicator).get_attribute("textContent")
    )
    assert not fluid_model_page.is_element_displayed(sort_up_icon), "Иконка прямой сортировки не должна отображаться"
    assert not fluid_model_page.is_element_displayed(sort_down_icon), "Иконка обратной сортировки не должна отображаться"


def test_column_sorting_behavior(created_json_version, fluid_model_page):
    """Рабочий
    Проверка поведения сортировки столбцов в таблице флюидов.
    Использует генераторы локаторов и методы fluid_model_page (фикстура возвращает экземпляр FluidModelTab).
    """
    grid_css = "#fluidModelGrid"
    col_id = "name"

    # 0. Сброс сортировки (используем метод класса, передаём grid_css)
    fluid_model_page.reset_sorting(col_id=col_id, grid_css=grid_css)

    # Локаторы через мини-функции
    sort_header = fluid_model_page.sort_header_locator(grid_css, col_id)
    sort_order_indicator = fluid_model_page.sort_order_indicator_locator(grid_css, col_id)

    # 1. Исходное состояние
    initial_values = fluid_model_page.get_name_column_values(max_rows=6, col_id=col_id, grid_css=grid_css)
    print(f"Исходные значения {col_id}: {initial_values}")

    # 2. Прямая сортировка (клик по заголовку)
    fluid_model_page.click(sort_header)
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "1" in (driver.find_element(*sort_order_indicator).get_attribute("textContent") or "")
    )

    ascending_values = fluid_model_page.get_name_column_values(max_rows=6, col_id=col_id, grid_css=grid_css)
    print(f"После прямой сортировки {col_id}: {ascending_values}")
    if ascending_values:
        assert ascending_values == sorted(ascending_values), "Должна быть сортировка по возрастанию"
        print('прямая сортировка успешна')

    before_desc = fluid_model_page.driver.find_element(
        By.CSS_SELECTOR, f"{grid_css} div.ag-row[aria-rowindex='2'] div[col-id='{col_id}']"
    ).text

    # 3. Обратная сортировка (ещё один клик)
    fluid_model_page.click(sort_header)
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "1" in (driver.find_element(*sort_order_indicator).get_attribute("textContent") or "")
    )
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: driver.find_element(
            By.CSS_SELECTOR, f"{grid_css} div.ag-row[aria-rowindex='2'] div[col-id='{col_id}']"
        ).text != before_desc
    )
    descending_values = fluid_model_page.get_name_column_values(max_rows=6, col_id=col_id, grid_css=grid_css)
    print(f"После обратной сортировки {col_id}: {descending_values}")
    if descending_values:
        assert descending_values == sorted(descending_values, reverse=True), "Должна быть сортировка по убыванию"
        print('обратная сортировка успешна')

    # 4. Сброс сортировки (ещё один клик)
    fluid_model_page.click(sort_header)
    WebDriverWait(fluid_model_page.driver, 10).until(
        lambda driver: "0" in (driver.find_element(*sort_order_indicator).get_attribute("textContent") or "")
    )

    final_values = fluid_model_page.get_name_column_values(max_rows=6, col_id=col_id, grid_css=grid_css)
    print(f"После сброса сортировки {col_id}: {final_values}")
