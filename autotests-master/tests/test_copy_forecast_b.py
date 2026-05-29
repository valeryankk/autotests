from pages.base_page import BasePage
from pages.create_forecast_modal_page import CreateForecastVersionModal

def test_create_button_disabled_without_copy_version_selected(create_forecast_modal_function):
    modal = create_forecast_modal_function
    modal.wait_until_modal_visible()

    # Заполнить остальные обязательные поля, кроме 'Версия'
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.creation_method_options)

    modal.is_element_displayed(modal.copy_source_version_field), "Поле 'Версия' не отображается"
    version_value = modal.get_field_value(modal.copy_source_version_field)
    assert version_value == "", "Поле 'Версия' должно быть пустым по умолчанию"

    assert modal.is_element_disabled(modal.save_button), "Кнопка 'Создать' не должна быть активной без выбора версии"

    modal.click_extra(modal.close_button)

def test_copy_mode_fields_visibility_and_defaults(create_forecast_modal_data):
    modal, forecast, year = create_forecast_modal_data
    modal.wait_until_modal_visible()
    
    # Шаг 1: Выбираем способ создания - "Копирование версии"
    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.combobox_locator)

    # Шаг 2: Проверяем, что появились дополнительные поля
    assert modal.is_element_displayed(modal.copy_source_do_field), "Поле 'ДО' не отображается"
    assert modal.is_element_displayed(modal.copy_source_forecast_field), "Поле 'Прогноз' не отображается"
    assert modal.is_element_displayed(modal.copy_source_year_field), "Поле 'Год' не отображается"
    assert modal.is_element_displayed(modal.copy_source_version_field), "Поле 'Версия' не отображается"

    # Шаг 3: Проверяем, что поле 'ДО' заблокировано
    assert modal.is_element_disabled(modal.copy_source_do_field), "Поле 'ДО' должно быть заблокировано"
    # Шаг 4: Проверяем, что 'Прогноз' и 'Год' выбраны по умолчанию
    forecast_value = modal.get_field_value(modal.copy_source_forecast_field)
    year_value = modal.get_field_value(modal.copy_source_year_field)
    assert forecast_value == forecast, "Поле 'Прогноз' должно иметь значение по умолчанию"
    assert year_value == year, "Поле 'Год' должно иметь значение по умолчанию"

    # Шаг 5: Проверяем, что поле 'Версия' пустое (ожидается выбор пользователем)
    version_value = modal.get_field_value(modal.copy_source_version_field)
    assert version_value == "", "Поле 'Версия' должно быть пустым по умолчанию"

    modal.click_extra(modal.close_button)


def test_successful_forecast_copy_creation(filled_form, forecast_registry_page):
    name_copy  = forecast_registry_page.select_first_forecast()

    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()
    modal.wait_until_modal_visible()

    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.creation_method_options)

    assert modal.is_element_displayed(modal.copy_source_do_field)
    assert modal.is_element_displayed(modal.copy_source_forecast_field)
    assert modal.is_element_displayed(modal.copy_source_year_field)
    assert modal.is_element_displayed(modal.copy_source_version_field)

    assert modal.is_element_disabled(modal.copy_source_do_field)

    # Выбор версии для копирования
    modal.select_from_combobox(modal.copy_source_version_field, name_copy, modal.combobox_locator)

    #проверка подтянулось ли какое то значение
    modal.wait_for_field_not_empty(modal.start_date_field)
    modal.wait_for_field_not_empty(modal.end_date_field)
    start_date = modal.get_field_value(modal.start_date_field)
    end_date = modal.get_field_value(modal.end_date_field)
    assert start_date != "", 'В поле "Дата начала расчета" не подтянулось значение выбранной версии'
    assert end_date != "", 'В поле "Дата конца расчета" не подтянулось значение выбранной версии'

    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    assert modal.is_element_enabled(modal.save_button)
    modal.click_extra(modal.create_button2)
    modal.wait_until_modal_disappears()

    success_alert = forecast_registry_page.wait_until_visible(forecast_registry_page.success_alert)
    assert "Версия прогноза успешно создана" in success_alert.text

    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name)

    #Выбираем версию с которой копировали 
    forecast_registry_page.select_forecast_by_name(name_copy)
    forecast_registry_page.click_extra(forecast_registry_page.edit_btn)
    
    #проверка подтянулось ли какое то корректное значение
    start_date_copy = modal.get_field_value(modal.start_date_field)
    end_date_copy = modal.get_field_value(modal.end_date_field)
    assert start_date == start_date_copy, 'В поле "Дата начала расчета" подтянулось неверное значение выбранной версии'
    assert end_date == end_date_copy, 'В поле "Дата конца расчета" не подтянулось неверное значение выбранной версии'

    modal.click_extra(modal.close_button)
    
    forecast_registry_page.delete_forecast_by_name(name)