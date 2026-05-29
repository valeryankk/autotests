import pytest
import json
from pages.common_pg_form_page import CommonPgForm
import os

def test_create_button_visible(authenticated_driver, base_url):
    page = CommonPgForm(authenticated_driver)
    page.open(base_url + 'X')
    assert page.wait_until_visible(page.create_button).is_displayed() and not page.is_create_button_enabled()

def test_autocomplete_selection_works(authenticated_driver, base_url):
    page = CommonPgForm(authenticated_driver)
    page.open(base_url + "X")
    page.select_first_from_autocomplete(page.enterprise_field)
    selected_value = page.get_text(page.enterprise_field)
    assert selected_value is not None

def load_autocomplete_data():
    # Путь: подняться на уровень выше, потом в testdata
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    file_path = os.path.join(base_dir, "testdata", "autocomplete_options.json")
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

autocomplete_data = load_autocomplete_data()

def generate_test_cases(data):
    return [
        (None, data["enterprise"][0], None, False),
        (None, None, data["forecast"][0], False),
        (data["year"][1], data["enterprise"][1], None, True),
        (data["year"][2], None, data["forecast"][1], True),
        (data["year"][1], data["enterprise"][1], data["forecast"][0], True),
    ]

@pytest.mark.parametrize(
    "year, enterprise, forecast, change_year",
    generate_test_cases(autocomplete_data)
)
def test_create_button_active_with_partial_fields(authenticated_driver, base_url, year, enterprise, forecast, change_year):
    page = CommonPgForm(authenticated_driver)
    page.open(base_url + "X")

    if change_year and year:
        page.select_from_autocomplete(page.year_field, year, enter_text=True)

    if enterprise:
        page.select_from_autocomplete(page.enterprise_field, enterprise, enter_text=False)

    if forecast:
        page.select_from_autocomplete(page.forecast_field, forecast, enter_text=False)

    if enterprise and forecast:
        assert page.is_create_button_enabled()
    else:
        assert not page.is_create_button_enabled()
