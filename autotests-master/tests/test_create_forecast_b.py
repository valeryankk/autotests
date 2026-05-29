def test_modal_subtitle(create_forecast_modal_data):
    modal, forecast, year = create_forecast_modal_data
    expected_subtitle = f"{forecast} {year}"
    actual_subtitle = modal.get_subtitle_text()
    assert actual_subtitle == expected_subtitle, f"Ожидался подзаголовок '{expected_subtitle}', но получили '{actual_subtitle}'"

def test_main_version_checkbox_behavior(create_forecast_modal_data):
    modal, forecast, _ = create_forecast_modal_data
    
    # Проверяем, что передан нужный тип прогноза
    assert forecast in ["БП", '0+12', '1+11', '2+10', '3+9', '4+8', '5+7', '6+6', '7+5', '8+4', '9+3', '10+2', '11+1', '12+0'], f"Ожидался прогноз 'БП или 0+12, 1+11, ..., 11+1, 12+0', но был '{forecast}'"

    assert modal.is_element_displayed(modal.main_version_lbl), "Чекбокс 'Основная версия' не отображается"

    # По умолчанию должен быть false
    assert modal.get_attribute(modal.main_version_checkbox, "ng-reflect-model", wait_visible=False) == "false", "Чекбокс должен быть снят по умолчанию"

    checkbox = modal.wait_until_visible(modal.main_version_lbl)

    checkbox.click()
    assert  modal.get_attribute(modal.main_version_checkbox, "ng-reflect-model", wait_visible=False) == "true", "Чекбокс должен быть отмечен после клика"

    checkbox.click()
    assert  modal.get_attribute(modal.main_version_checkbox, "ng-reflect-model", wait_visible=False) == "false", "Чекбокс должен быть снят после повторного клика"  


