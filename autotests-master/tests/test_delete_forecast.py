
from pages.base_page import BasePage

def test_successful_forecast_delete(created_forecast, forecast_registry_page):
    # Создание новой версии прогноза
    modal, name = created_forecast
    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), f"Версия прогноза '{name}' не появилась в реестре"

    # Выбор версии и активация кнопки удаления
    forecast_registry_page.select_forecast_by_name(name)
    assert forecast_registry_page.is_element_enabled(forecast_registry_page.delete), "Кнопка 'Удалить' должна быть активной"

    # Отмена удаления — проверка, что версия не исчезла
    forecast_registry_page.click_extra(forecast_registry_page.delete)
    confirm_text = forecast_registry_page.wait_until_visible(forecast_registry_page.confirm_text)
    assert f'Вы действительно хотите удалить версию прогноза "{name}"?' in confirm_text.text, "Некорректный текст подтверждения"

    forecast_registry_page.click_extra(forecast_registry_page.cancel_delete_btn)
    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), "Версия не должна была удалиться после отказа"

    # Удаление
    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(forecast_registry_page.delete)
    forecast_registry_page.click_extra(forecast_registry_page.confirm_delete_btn)

    assert forecast_registry_page.wait_until_forecast_disappears(name), "Версия не удалилась после подтверждения" 

    # Проверка уведомления об успешном удалении
    success_alert = forecast_registry_page.wait_until_visible(forecast_registry_page.success_delete_alert)
    assert success_alert is not None, "Уведомление об успешном удалении не появилось"
    assert "Версия прогноза успешно удалена" in success_alert.text.strip(), f"Ожидался текст 'Версия прогноза успешно удалена', но получили: '{success_alert.text.strip()}'"
