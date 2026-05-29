
import pytest
from pages.base_page import BasePage

def test_successful_forecast_creation(create_forecast_modal_function, forecast_registry_page):
    # Явно открываем модалку
    
    modal = create_forecast_modal_function
    modal.wait_until_modal_visible()

    name = BasePage.generate_random_name()

    # Далее заполняем форму, проверяем, создаём
    modal.set_text_input(modal.name_input, name)
    assert modal.is_create_btn_disabled(), "Кнопка 'Создать' должна быть не активна при незаполненных обязательных полях"
    modal.set_start_date("01.01.2025")
    modal.set_end_date("01.01.2026")

    assert modal.get_field_value(modal.creation_method_field) == "Ручной ввод"
    assert not modal.is_create_btn_disabled(), "Кнопка 'Создать' должна быть активна после заполнения обязательных полей"
    modal.click_extra(modal.create_button2)

    modal.wait_until_modal_disappears()

    #Проверка уведомления
    success_alert = forecast_registry_page.wait_until_visible(forecast_registry_page.success_alert)
    assert success_alert is not None, "Уведомление об успешном создании не появилось"

    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), f"Версия прогноза '{name}' не появилась в реестре"
    try:
        assert forecast_registry_page.is_forecast_first_in_list(name), f"Созданная версия '{name}' не отображается первой в реестре"
    finally:
        # Удаляем независимо от результата
        forecast_registry_page.delete_forecast_by_name(name)



@pytest.mark.parametrize("close_method", ["cancel", "cross"])
def test_cancel_or_cross_does_not_create_forecast(create_forecast_modal_function, forecast_registry_page, close_method):
    modal = create_forecast_modal_function
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()

    # Закрываем форму выбранным способом
    if close_method == "cancel":
        # Заполняем только одно поле, чтобы имитировать неполную форму
        modal.set_text_input(modal.name_input, name)
        modal.click_extra(modal.close_button)
    elif close_method == "cross":
        # Не заполняем форму
        name_field = modal.wait_until_visible(modal.name_input)
        name_field.get_attribute("value")
        name = modal.click_extra(modal.close_cross)
    else:
        pytest.fail(f"Неизвестный способ закрытия: {close_method}")

    # Ждём, пока форма исчезнет
    modal.wait_until_modal_disappears()

    try:
        # Проверяем, что версия прогноза не появилась
        assert not forecast_registry_page.wait_for_forecast_to_appear_in_list(name), f"Версия прогноза '{name}' появилась в реестре"
    finally:
        if forecast_registry_page.is_forecast_present(name):
            forecast_registry_page.delete_forecast_by_name(name)


