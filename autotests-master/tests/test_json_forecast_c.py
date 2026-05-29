'''запускать через --user в терминале'''

import pytest

def test_creation_method_json_option_visibility(reset_forecast_modal, request):
    """Проверка наличия/отсутствия опции 'Загрузка из JSON' для разных ролей."""
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()

    # Открываем выпадающий список
    field = modal.wait_until_visible(modal.creation_method_field)
    field.click()
    options = modal.wait_until_visible_all(modal.creation_method_options)
    option_texts = [opt.text.strip() for opt in options]
    users = [
    "x", "y", "z"]
    current_user = request.config.getoption("--user")

    if current_user == "x":
        assert "Загрузка из JSON" in option_texts, (
            f"Для роли {current_user} должна быть опция 'Загрузка из JSON', но её нет"
        )
    elif current_user in users:
        assert "Загрузка из JSON" not in option_texts, (
            f"Для роли {current_user} не должно быть опции 'Загрузка из JSON', но она есть: {option_texts}"
        )
    else:
        pytest.skip(f"Роль {current_user} пока не поддерживается этим тестом")
