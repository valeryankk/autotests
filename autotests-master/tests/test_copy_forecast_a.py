#Можно сделать так - будет искать версию с непустыми флюидами и копировать ее (фикстура - copied_version_name)
#Реализация сейчас - создает из json и копирует ее(чтобы корректнне проверить копирование вкладок)

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

    
def test_check_fluid_model_tab_data_after_copy(copied_json_version_name, forecast_registry_page, fluid_model_page): 
    # имена версий 
    name = copied_json_version_name["name"]
    name_orig = copied_json_version_name["name_orig"]

    #выбор версии и получение информации с вкладки
    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(fluid_model_page.fluid_model_tab)

    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass

    list_name_new = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.fluid_model_rows,
        header_keywords= fluid_model_page.fluid_model_header)
    
    forecast_registry_page.select_forecast_by_name(name_orig)
    forecast_registry_page.click_extra(fluid_model_page.fluid_model_tab)
    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass
    
    list_name_orig = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.fluid_model_rows,
        header_keywords=fluid_model_page.fluid_model_header
    )

    assert list_name_orig == list_name_new, f"Вкладка МОДЕЛЬ ФЛЮИДА скопировалась некорректно. Ожидалось {list_name_orig}, получили {list_name_new}"


def test_check_plast_model_mathbalance_tab_data_after_copy(copied_json_version_name, forecast_registry_page, fluid_model_page): 
    name = copied_json_version_name["name"]
    name_orig = copied_json_version_name["name_orig"]

    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(fluid_model_page.plast_model_tab)
    forecast_registry_page.click_extra(fluid_model_page.plast_model_tab_mathbalance)

    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(lambda d: any(row.text.strip() for row in d.find_elements(*fluid_model_page.plast_model_rows)))
    except TimeoutException: 
        pass

    list_name_new = fluid_model_page.get_model_rows_as_lists(
        grid_id="layerModelZoneGrid",
        row_locator=fluid_model_page.plast_model_rows,
        header_keywords=fluid_model_page.plast_model_header_mathbalance
    )

    forecast_registry_page.select_forecast_by_name(name_orig)
    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(lambda d: any(row.text.strip() for row in d.find_elements(*fluid_model_page.plast_model_rows)))
    except TimeoutException: 
        pass

    list_name_orig = fluid_model_page.get_model_rows_as_lists(
        grid_id="layerModelZoneGrid",
        row_locator=fluid_model_page.plast_model_rows,
        header_keywords=fluid_model_page.plast_model_header_mathbalance
    )

    assert list_name_orig == list_name_new, f"Вкладка МОДЕЛЬ ПЛАСТА - МАТБАЛАНС скопировалась некорректно. Ожидалось {list_name_orig}, получили {list_name_new}"


def test_check_plast_model_polinom_tab_data_after_copy(copied_json_version_name, forecast_registry_page, fluid_model_page):
    name = copied_json_version_name["name"]
    name_orig = copied_json_version_name["name_orig"]

    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(fluid_model_page.plast_model_tab)
    forecast_registry_page.click_extra(fluid_model_page.plast_model_tab_polinom)

    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass

    list_name_new = fluid_model_page.get_model_rows_as_lists(
        grid_id="layerModelPolynomialGrid",
        row_locator=fluid_model_page.plast_model_rows_polynom,
        header_keywords=fluid_model_page.plast_model_header_polinom
    )

    forecast_registry_page.select_forecast_by_name(name_orig)
    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass

    list_name_orig = fluid_model_page.get_model_rows_as_lists(
        grid_id="layerModelPolynomialGrid",
        row_locator=fluid_model_page.plast_model_rows_polynom,
        header_keywords=fluid_model_page.plast_model_header_polinom
    )

    assert list_name_orig == list_name_new, f"Вкладка МОДЕЛЬ ПЛАСТА - ПОЛИНОМ скопировалась некорректно. Ожидалось {list_name_orig}, получили {list_name_new}"


def test_check_wells_tab_data_after_copy(copied_json_version_name, forecast_registry_page, fluid_model_page):
    name = copied_json_version_name["name"]
    name_orig = copied_json_version_name["name_orig"]

    forecast_registry_page.select_forecast_by_name(name)
    forecast_registry_page.click_extra(fluid_model_page.wells_tab)

    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass

    list_name_new = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.wells_rows,
        header_keywords=fluid_model_page.wells_header
    )
    forecast_registry_page.select_forecast_by_name(name_orig)

    try:
        WebDriverWait(forecast_registry_page.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[col-id="checkbox"]')))
    except TimeoutException: 
        pass

    list_name_orig = fluid_model_page.get_model_rows_as_lists(
        grid_id="fluidModelGrid",
        row_locator=fluid_model_page.wells_rows,
        header_keywords=fluid_model_page.wells_header
    )

    assert list_name_orig == list_name_new, f"Вкладка СКВАЖИНЫ скопировалась некорректно. Ожидалось {list_name_orig}, получили {list_name_new}"



