
def test_successful_forecast_edit(created_forecast, forecast_registry_page): #валидное редактирование
    modal, original_name = created_forecast
    
    forecast_registry_page.wait_for_forecast_to_appear_in_list(original_name)

    forecast_registry_page.select_forecast_by_name(original_name)
    forecast_registry_page.click_extra(forecast_registry_page.edit_btn)
    modal.wait_until_modal_visible()

    new_name = f"{original_name}_edited"
    modal.set_text_input(modal.name_input, new_name)

    save_button_text = forecast_registry_page.wait_until_visible(modal.save_button)
    assert save_button_text.text == 'Сохранить', f"Неверный текст на кнопке. Ожидалось 'Сохранить', получили {save_button_text.text}"

    modal.click_extra(modal.save_button)
    modal.wait_until_modal_disappears()

    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(new_name), "Название версии не изменилось в реестре"
    assert forecast_registry_page.wait_until_forecast_disappears(original_name), "Предыдущее название не исчезло из реестра"

    success_alert = forecast_registry_page.wait_until_visible(forecast_registry_page.success_edit_alert)
    assert "Версия прогноза успешно отредактирована" in success_alert.text, f"Неверный текст на кнопке. Получили {success_alert.text}"

    forecast_registry_page.delete_forecast_by_name(new_name)



 
def test_edit_forecast_cancel(created_forecast, forecast_registry_page): #отмена редактирования
    modal, name = created_forecast
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)

    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(forecast_registry_page.edit_btn)
    modal.wait_until_modal_visible()
    modal.set_text_input(modal.name_input, name + "_cancel")
    modal.click_extra(modal.close_button)
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)

    assert forecast_registry_page.wait_until_forecast_disappears(name + "_cancel")
    forecast_registry_page.delete_forecast_by_name(name)

def test_edit_forecast_validation(created_forecast, forecast_registry_page): #невалидное редактирование
    modal, name = created_forecast
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)

    forecast_registry_page.select_forecast_by_name(name)

    forecast_registry_page.click_extra(forecast_registry_page.edit_btn)
    modal.wait_until_modal_visible()
    modal.remove_and_fill(modal.name_input, "")
 
    assert modal.is_element_disabled(modal.save_button), "Кнопка 'Сохранить' активна при некорректных данных"
    modal.click_extra(modal.close_button)
    assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), f"Версия прогноза {name} не появилась в реестре"

    forecast_registry_page.delete_forecast_by_name(name)
 

def test_edit_forecast_no_change(created_forecast, forecast_registry_page): #редактирование без изменений
    modal, name = created_forecast

    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)
    forecast_registry_page.select_forecast_by_name(name)

    forecast_registry_page.click_extra(forecast_registry_page.edit_btn)
    modal.wait_until_modal_visible()
    assert modal.is_element_enabled(modal.save_button), "Кнопка 'Сохранить' активна должна быть активна при корректных данных"

    modal.click_extra(modal.save_button)
    modal.wait_until_modal_disappears()
    try:
        success_alert = forecast_registry_page.wait_until_visible(forecast_registry_page.success_edit_alert)
        assert "Версия прогноза успешно отредактирована" in success_alert.text, f"Неверный текст на кнопке. Получили {success_alert.text}"
        assert forecast_registry_page.wait_for_forecast_to_appear_in_list(name), f"Версия прогноза {name} не появилась в реестре"

    finally:
        if forecast_registry_page.is_forecast_present(name):
            forecast_registry_page.delete_forecast_by_name(name)

