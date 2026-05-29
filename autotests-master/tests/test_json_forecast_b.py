import os
from pages.base_page import BasePage
from pages.create_forecast_modal_page import CreateForecastVersionModal

def test_create_after_correct_check(filled_form, forecast_registry_page, fluid_model_page): #корректный файл
    name = BasePage.generate_random_name()

    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()
    modal.set_text_input(modal.name_input, name)

    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "27.08.json") 
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = modal.upload_file(file_path)
    
    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    modal.wait.until(lambda d: modal.get_input_value(modal.json_results_field).strip() != "")

    modal.wait_until_clickable(modal.create_button2)
    modal.click_extra(modal.create_button2)
    try:
        assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), "Название версии не появилось в реестре"
        assert forecast_registry_page.is_forecast_first_in_list(name), f"Созданная версия '{name}' не отображается первой в реестре"
    finally:
        forecast_registry_page.delete_forecast_by_name(name)

def test_correct_creating_not_empty(filled_form, forecast_registry_page, fluid_model_page): #корректный файл
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)

    # 1. Выбираем метод "Загрузка из JSON"
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "27.08.json") 
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = modal.upload_file(file_path)
    
    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    modal.is_element_enabled(modal.create_button2)
    modal.click_extra(modal.create_button2)

    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)
    forecast_registry_page.select_forecast_by_name(name)
    fluid_model_page.click_extra(fluid_model_page.fluid_model_tab)
    try:
        assert fluid_model_page.is_fluid_model_list_not_empty(), "Таблица моделей флюида пуста, но должна содержать данные из JSON"
    finally:
        forecast_registry_page.delete_forecast_by_name(name)


