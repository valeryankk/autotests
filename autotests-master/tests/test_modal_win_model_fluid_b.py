from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from pages.create_fluid_model_modal import CreateFluidModelModal

def test_cannot_create_duplicate_name_fluid_in_another_forecast(two_forecasts_with_fluid, fluid_model_page, forecast_registry_page, filled_form):
    """
    Проверка: разрешено создавать флюиды с одинаковым наименованием в разных версиях прогноза.
    """
    data = two_forecasts_with_fluid
    name_forecast_2 = data["name_forecast_2"]
    unique_name = data["name_f"]
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name_forecast_2)
    forecast_registry_page.select_forecast_by_name(name_forecast_2)
    
    # ---- 2. Пытаемся создать второй флюид с тем же именем ----
    fluid_model_page.click_extra(fluid_model_page.fluid_model_tab)
    fluid_model_page.click_extra(fluid_model_page.zonal_model)
    fluid_model_page.click_extra(fluid_model_page.create_button)
    modal2 = CreateFluidModelModal(filled_form.driver)
    modal2.wait_until_visible(modal2.modal)

    modal2.set_text_input(modal2.name_field, unique_name)  # то же имя
    modal2.select_from_combobox(modal2.type_fluid, "Газовая", modal2.options_from_dropdown)    
    modal2.type(modal2.pressure_field, "150")
    modal2.type(modal2.temperature_field, "250")
    modal2.type(modal2.density_gas_field, "10")

    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_A, "1")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_B, "1")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_C, "1")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_D, "1")

    modal2.click_extra(modal2.create_button3)
    modal2.wait_long_until_element_disappears(modal2.modal)
    check = modal2.is_element_displayed(modal2.error_locator)

    # ---- 3. Проверяем, что окно закрылось и не появилось сообщение об ошибке ----
    assert not check, 'Появилось сообщение об ошибке при создании при модели флюида, хотя не ожидалось'
    if check:
        modal2.close_error_notification(modal2.error_locator)
    # Закрываем модальное окно
    
    
    # ---- 4. Проверяем, что в реестре остался только один флюид с таким именем ----
    fluids = fluid_model_page.get_all_fluids_by_name(unique_name)
    assert len(fluids) == 1, f"Ожидалось 1 флюид '{unique_name}', но найдено {len(fluids)}"


def test_cannot_create_duplicate_name_fluid(two_forecasts_with_fluid, fluid_model_page, filled_form, forecast_registry_page):
    """
    Проверка: запрещено создавать флюиды с одинаковым наименованием в текущей версии прогноза.
    """
    data = two_forecasts_with_fluid
    unique_name = data["name_f"]
    name_forecast = data["name_forecast"]
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name_forecast)
    forecast_registry_page.select_forecast_by_name(name_forecast)
    
    # ---- 2. Пытаемся создать второй флюид с тем же именем ----
    fluid_model_page.click_extra(fluid_model_page.fluid_model_tab)
    fluid_model_page.click_extra(fluid_model_page.zonal_model)
    fluid_model_page.click_extra(fluid_model_page.create_button)
    modal2 = CreateFluidModelModal(filled_form.driver)
    modal2.wait_until_visible(modal2.modal)

    modal2.set_text_input(modal2.name_field, unique_name)  # то же имя
    modal2.select_from_combobox(modal2.type_fluid, "Газовая", modal2.options_from_dropdown)    
    modal2.type(modal2.pressure_field, "150")
    modal2.type(modal2.temperature_field, "250")
    modal2.type(modal2.density_gas_field, "10")

    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_A, "0")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_B, "0")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_C, "0")
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_D, "0")

    modal2.click_extra(modal2.create_button3)

    # ---- 3. Проверяем, что окно не закрылось и появилось сообщение об ошибке ----
    error_alert = modal2.wait_until_visible(modal2.error_locator)
    assert "Уже существует модель флюида" in error_alert.text, "Ожидалось сообщение об ошибке про дублирование"
    modal2.close_error_notification(modal2.error_locator)
    
    # Закрываем модальное окно
    modal2.click(modal2.close_button)
    modal2.wait_long_until_element_disappears(modal2.modal)

    # ---- 4. Проверяем, что в реестре остался только один флюид с таким именем ----
    fluids = fluid_model_page.get_all_fluids_by_name(unique_name)
    assert len(fluids) == 1, f"Ожидалось 1 флюид '{unique_name}', но найдено {len(fluids)}"

def test_cannot_create_duplicate_fluid(two_forecasts_with_fluid, fluid_model_page, filled_form, forecast_registry_page):
    """
    Проверка: запрещено создавать флюиды с одинаковыми данными, но с разными именами в текущей версии прогноза.
    """
    data = two_forecasts_with_fluid
    unique_name = BasePage.generate_random_name('Идентичный флюид')
    name_forecast = data["name_forecast"]
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name_forecast)
    forecast_registry_page.select_forecast_by_name(name_forecast)
    
    # ---- 2. Пытаемся создать второй флюид с теми же данными----
    fluid_model_page.click_extra(fluid_model_page.fluid_model_tab)
    fluid_model_page.click_extra(fluid_model_page.zonal_model)
    fluid_model_page.click_extra(fluid_model_page.create_button)
    modal2 = CreateFluidModelModal(filled_form.driver)
    modal2.wait_until_visible(modal2.modal)

    modal2.set_text_input(modal2.name_field, unique_name)  
    modal2.select_from_combobox(modal2.type_fluid, data["type_f"], modal2.options_from_dropdown)    
    modal2.type(modal2.pressure_field, data["pressure_f"])
    modal2.type(modal2.temperature_field, data["temperature_f"])
    modal2.type(modal2.density_gas_field, data["density_f"])

    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_A, data["coef_a"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_B, data["coef_b"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_C, data["coef_c"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_D, data["coef_d"])

    modal2.click_extra(modal2.create_button3)

    # ---- 3. Проверяем, что окно не закрылось и появилось сообщение об ошибке ----
    try:
        modal2.wait_until_visible(modal2.error_locator)
    except:
        pass
    error_alert = modal2.wait_until_visible(modal2.error_locator)
    assert "Уже существует модель флюида с идентичными параметрами" in error_alert.text, "Ожидалось сообщение об ошибке про дублирование"
    assert modal2.is_element_displayed(modal2.modal), 'Модальное окно закрылось после некорректной попытки создания, хотя это не ожидалось'
    
    modal2.close_error_notification(modal2.error_locator)
    # Закрываем модальное окно
    modal2.click(modal2.cancel_button)
    modal2.wait_long_until_element_disappears(modal2.modal)

    # ---- 4. Проверяем, что в реестре остался только один флюид с таким именем ---- !!!!!!
    fluids = fluid_model_page.get_all_fluids_by_name(unique_name)
    assert len(fluids) == 0, f"Ожидалось 0 флюидов '{unique_name}', но найдено {len(fluids)}"

def test_cannot_create_duplicate_fluid_in_another_version(two_forecasts_with_fluid, fluid_model_page, filled_form, forecast_registry_page):
    """
    Проверка: разрешено создавать флюиды с одинаковыми данными, но с разными именами в разных версиях прогноза.
    """
    data = two_forecasts_with_fluid
    unique_name = BasePage.generate_random_name('Флюид')
    name_forecast = data["name_forecast_2"]
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name_forecast)
    forecast_registry_page.select_forecast_by_name(name_forecast)
    
    # ---- 2. Пытаемся создать второй флюид с теми же данными ----
    fluid_model_page.click_extra(fluid_model_page.fluid_model_tab)
    fluid_model_page.click_extra(fluid_model_page.zonal_model)
    fluid_model_page.click_extra(fluid_model_page.create_button)
    modal2 = CreateFluidModelModal(filled_form.driver)
    modal2.wait_until_visible(modal2.modal)

    modal2.set_text_input(modal2.name_field, unique_name)  
    modal2.select_from_combobox(modal2.type_fluid, data["type_f"], modal2.options_from_dropdown)    
    modal2.type(modal2.pressure_field, data["pressure_f"])
    modal2.type(modal2.temperature_field, data["temperature_f"])
    modal2.type(modal2.density_gas_field, data["density_f"])

    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_A, data["coef_a"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_B, data["coef_b"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_C, data["coef_c"])
    modal2.edit_grid_cell_via_keys(modal2.сondensation_coefficient_D, data["coef_d"])

    modal2.wait_until_clickable(modal2.create_button3)
    modal2.click_extra(modal2.create_button3)
    try:
        modal2.wait_until_visible(modal2.error_locator)
    except:
        pass
    # ---- 3. Проверяем, что окно закрылось и не появилось сообщение об ошибке ----
    assert not modal2.is_element_displayed(modal2.error_locator), 'Появилось сообщение об ошибке, при корректном создании версии'
    modal2.wait_long_until_element_disappears(modal2.modal)

    # ---- 4. Проверяем, что в реестре остался только один флюид с таким именем ----
    fluids = fluid_model_page.get_all_fluids_by_name(unique_name)
    assert len(fluids) == 1, f"Ожидалось 1 флюид '{unique_name}', но найдено {len(fluids)}"


def test_fluid_registry_has_mark_column_header_empty(two_forecasts_with_fluid, fluid_model_page, filled_form, forecast_registry_page):
    """
    8. В таблице присутствует колонка 'Отметка'
    Проверяем наличие хедера колонки с col-id='checkbox' в пустом реестре
    """
    data = two_forecasts_with_fluid
    name_forecast = data["name_forecast_2"]
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name_forecast)
    forecast_registry_page.select_forecast_by_name(name_forecast)
    header_checkbox = fluid_model_page.driver.find_elements(
        By.CSS_SELECTOR,
        "div.ag-header-cell[col-id='checkbox']"
    )
    assert len(header_checkbox) > 0, "В таблице отсутствует колонка 'Отметка' (col-id='checkbox')"


