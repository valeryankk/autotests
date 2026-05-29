import json
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.login_page import LoginPage
from pages.forecast_registry_page import ForecastRegistryPage
from pages.common_pg_form_page import CommonPgForm
from pages.create_forecast_modal_page import CreateForecastVersionModal
from pages.create_fluid_model_modal import CreateFluidModelModal
from pages.fluid_modal_tab_page import FluidModelTab
from pages.base_page import BasePage

# Загрузка конфигурации из config.json
def load_config():
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)

ROLES = [
    "x", "y", "z"
]

def pytest_addoption(parser):
    roles_str = "Available roles:\n  " + ", ".join(ROLES)
    parser.addoption("--env", action="store", default="test", help="Environment: test, uat")
    parser.addoption("--user", action="store", default="admin_user",  help=roles_str)

#загрузка невалидных пароль/логин из invalid_login_data.json
def load_invalid_login_data():
    filepath = os.path.join(os.path.dirname(__file__), "testdata", "invalid_login_data.json")
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)

# Фикстура возвращает список пар пароль+логин
@pytest.fixture(scope="module")
def invalid_login_data():
    return load_invalid_login_data()

@pytest.fixture(scope="session")
def config(request):
    env = request.config.getoption("--env")
    data = load_config()

    if env not in data:
        pytest.fail(f"Unknown environment: {env}")

    # Вставляем активное окружение как подсловарь:
    data["env_config"] = data[env]
    return data

@pytest.fixture(scope="session")
def base_url(config):
    return config["env_config"]["base_url"]


@pytest.fixture(scope="session")
def login_url(config):
    return config["env_config"]["login_url"]

@pytest.fixture(scope="session")
def credentials(config, request):
    user_type = request.config.getoption("--user", default="default_user")
    creds = config["credentials"].get(user_type)
    if creds is None:
        pytest.fail(f"Unknown user type: {user_type}")
    return creds

@pytest.fixture
def driver(): # используется в тестах авторизации - не надо предварительно авторизироваться
    """Фикстура для запуска и закрытия браузера Chrome"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    #options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def authenticated_driver(credentials, base_url, login_url): # одна авторизация на весь тест
    """Фикстура: авторизованный Chrome-драйвер на сессию"""
    options = Options()
    options.add_argument("--start-maximized")
    #options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    page = LoginPage(driver, base_url, login_url)
    page.open()
    page.login(credentials["username"], credentials["password"])

    yield driver

    driver.quit()

#загрузка для пг

@pytest.fixture(scope="session")
def autocomplete_data():
    file_path = os.path.join(os.path.dirname(__file__), "testdata", "autocomplete_options.json")
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


from selenium.webdriver.support.ui import WebDriverWait

@pytest.fixture(scope="module")
def common_pg_form_create(authenticated_driver, base_url):
    page = CommonPgForm(authenticated_driver)
    WebDriverWait(authenticated_driver, 20).until(lambda d: "СБП - ГТМ-Факт" in d.title)
    page.open(base_url + "Xurl")
    WebDriverWait(authenticated_driver, 20).until(lambda d: "СБП - Природный газ" in d.title)
    return page


@pytest.fixture(scope="module")
def filled_form(common_pg_form_create, autocomplete_data):
    page = common_pg_form_create

    year_value = autocomplete_data["year"][0]
    enterprise_value = autocomplete_data["enterprise"][0]
    forecast_value = autocomplete_data["forecast"][0]

    page.select_from_autocomplete(page.year_field, year_value, enter_text=True)
    page.select_from_autocomplete(page.enterprise_field, enterprise_value, enter_text=True)
    page.select_from_autocomplete(page.forecast_field, forecast_value, enter_text=True)

    return page


@pytest.fixture(scope="module")
def filled_form_data(common_pg_form_create):
    page = common_pg_form_create

    enterprise_value = "enterprise_valueX"
    forecast_value = "БП"
    year_value = '2017'

    if enterprise_value in common_pg_form_create.get_attribute(page.enterprise_field, "value"):
        pass
    else:
        page.select_from_autocomplete(page.enterprise_field, enterprise_value, enter_text=True)

    if forecast_value in common_pg_form_create.get_attribute(page.year_field, "value"):
        pass
    else:
        page.select_from_autocomplete(page.year_field, year_value, enter_text=True)

    if year_value in common_pg_form_create.get_attribute(page.forecast_field, "value"):
        pass
    else:
        page.select_from_autocomplete(page.forecast_field, forecast_value, enter_text=True)

    return {
        "page": common_pg_form_create,
        "year": year_value,
        "forecast": forecast_value,
        "enterprise": enterprise_value,
    }

@pytest.fixture(scope="module")
def create_forecast_modal(filled_form):
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()
    return modal

@pytest.fixture
def create_forecast_modal_function(filled_form):
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()

    return modal

@pytest.fixture
def create_fluid_modal_function(filled_form):
    filled_form.click_create_button()
    modal = CreateFluidModelModal(filled_form.driver)
    modal.wait_until_modal_visible()

    return modal

@pytest.fixture(scope="module")
def created_version(filled_form, authenticated_driver):
    """Создаёт новую версию прогноза (без JSON) и отдаёт её имя, удаляет после тестов."""
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()

    modal.set_text_input(modal.name_input, name)
    modal.set_start_date("01.01.2025")
    modal.set_end_date("01.01.2026")
    modal.click_extra(modal.create_button2)
    modal.wait_long_until_element_disappears(modal.create_form)
    forecast_registry_page = ForecastRegistryPage(authenticated_driver)
    forecast_registry_page.select_forecast_by_name(name)

    yield name

    forecast_registry_page.delete_forecast_by_name(name)


@pytest.fixture
def create_fluid_modal(authenticated_driver, created_version, forecast_registry_page, fluid_model_page):
    """
    Открывает вкладку 'Модели флюида' внутри ранее созданной версии прогноза
    и возвращает модальное окно 'Создание флюида'.
    """
    # открываем страницу реестра
    registry_page = forecast_registry_page
    registry_page.select_forecast_by_name(created_version)

    # кликаем по вкладке "МОДЕЛИ ФЛЮИДА"
    fluid_page = FluidModelTab(authenticated_driver)
    fluid_page.click(fluid_page.fluid_model_tab)

    # нажимаем кнопку "Создать" → модальное окно
    fluid_page.click(fluid_page.create_button)
    modal = CreateFluidModelModal(authenticated_driver)
    modal.wait_until_visible(modal.modal)

    yield modal

    modal.close_all_modals_if_present()



@pytest.fixture(scope="module")
def created_json_version(filled_form, authenticated_driver):
    forecast_registry_page = ForecastRegistryPage(authenticated_driver)
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)
    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'tests', "27.08.json")
    assert os.path.exists(file_path), f"Файл {file_path} не найден"
    file_name = modal.upload_file(file_path)

    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    modal.wait.until(lambda d: modal.get_input_value(modal.json_results_field).strip() != "")

    modal.wait_until_clickable(modal.create_button2)
    modal.click_extra(modal.create_button2)
    modal.wait_long_until_element_disappears(modal.create_form)
    forecast_registry_page.select_forecast_by_name(name)

    yield name
    forecast_registry_page.wait_for_forecast_to_appear_in_list(name)
    forecast_registry_page.delete_forecast_by_name(name)


@pytest.fixture
def create_forecast_modal_data(filled_form_data):

    page = filled_form_data["page"]
    forecast = filled_form_data["forecast"]
    year = filled_form_data["year"]

    page.click_create_button()
    modal = CreateForecastVersionModal(page.driver)
    modal.wait_until_modal_visible()

    # Передаём данные в тест
    yield modal, forecast, year

    modal.click_extra(modal.close_button)


@pytest.fixture
def reset_forecast_modal(filled_form):
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()

    yield modal

    modal.click_extra(modal.close_button)

@pytest.fixture
def forecast_registry_page(authenticated_driver):
    return ForecastRegistryPage(authenticated_driver)

@pytest.fixture
def fluid_model_page(authenticated_driver):
    return FluidModelTab(authenticated_driver)




@pytest.fixture
def created_forecast(create_forecast_modal_function):# создание версии
    modal = create_forecast_modal_function
    modal.wait_until_modal_visible()

    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.set_start_date("01.01.2025")
    modal.set_end_date("01.01.2026")
    modal.click_extra(modal.create_button2)

    modal.wait_until_modal_disappears()

    return modal, name


@pytest.fixture(scope="module")
def copied_version_name(authenticated_driver, filled_form):
    '''
    Фикстура для проверки копирования версии
    - Находит непустую версию Х
    - Создает новую версию, копируя версию Х
    - Возвращает словарь - имя созданной версии и имя копируемой версии
    - Удаляет версию после завершения всех тестов
    '''

    forecast_registry_page = ForecastRegistryPage(authenticated_driver)
    fluid_model_page = FluidModelTab(authenticated_driver)

    # 1. Найти версию с непустой моделью
    full_name_copy = forecast_registry_page.find_first_non_empty_fluid_model_version_name(fluid_model_page)
    name_copy = full_name_copy

    # 7. Создание новой версии
    forecast_registry_page.click_extra(forecast_registry_page.create_button)
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()

    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.creation_method_options)
    modal.select_from_combobox(modal.copy_source_version_field, name_copy, modal.combobox_locator)
    modal.click_extra(modal.create_button2)
    modal.wait_long_until_element_disappears(modal.create_form)
    forecast_registry_page.click_extra(fluid_model_page.fluid_model_tab)

    # Возврат
    yield {
        "name_orig": name_copy,
        "name": name
    }

    # Очистка
    #
    forecast_registry_page.delete_forecast_by_name(name)

@pytest.fixture(scope="module")
def copied_json_version_name(authenticated_driver, filled_form):
    '''
    Фикстура для проверки копирования версии
    - Находит непустую версию Х
    - Создает новую версию, копируя версию Х
    - Возвращает словарь - имя созданной версии и имя копируемой версии
    - Удаляет версию после завершения всех тестов
    '''

    forecast_registry_page = ForecastRegistryPage(authenticated_driver)
    filled_form.click_create_button()
    modal1 = CreateForecastVersionModal(filled_form.driver)
    modal1.wait_until_modal_visible()
    name_copy = BasePage.generate_random_name()
    modal1.set_text_input(modal1.name_input, name_copy)
    modal1.select_from_combobox(modal1.creation_method_field, "Загрузка из JSON", modal1.creation_method_options)
    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'tests', "27.08.json")
    assert os.path.exists(file_path), f"Файл {file_path} не найден"
    file_name = modal1.upload_file(file_path)

    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal1.wait_until_clickable(modal1.check_btn)
    modal1.click_extra(modal1.check_btn)
    modal1.wait.until(lambda d: modal1.get_input_value(modal1.json_results_field).strip() != "")

    modal1.wait_until_clickable(modal1.create_button2)
    modal1.click_extra(modal1.create_button2)
    modal1.wait_long_until_element_disappears(modal1.create_form)



    forecast_registry_page = ForecastRegistryPage(authenticated_driver)
    fluid_model_page = FluidModelTab(authenticated_driver)

    # 1. Найти версию с непустой моделью


    full_name_copy = forecast_registry_page.find_first_non_empty_fluid_model_version_name(fluid_model_page)
    name_copy = full_name_copy

    # 7. Создание новой версии
    forecast_registry_page.click_extra(forecast_registry_page.create_button)
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()

    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.creation_method_options)
    modal.select_from_combobox(modal.copy_source_version_field, name_copy, modal.combobox_locator)
    modal.click_extra(modal.create_button2)
    modal.wait_long_until_element_disappears(modal.create_form)
    forecast_registry_page.click_extra(fluid_model_page.fluid_model_tab)

    # Возврат
    yield {
        "name_orig": name_copy,
        "name": name
    }

    # Очистка
    #
    forecast_registry_page.delete_forecast_by_name(name)

@pytest.fixture(scope="module")
def two_forecasts_with_fluid(authenticated_driver, filled_form):
    registry = ForecastRegistryPage(authenticated_driver)

    # ---------- Первая версия прогноза ----------
    filled_form.click_create_button()
    modal = CreateForecastVersionModal(filled_form.driver)
    modal.wait_until_modal_visible()

    name_forecast = BasePage.generate_random_name('Автотест с флюидом')
    modal.set_text_input(modal.name_input, name_forecast)
    modal.set_start_date("01.01.2025")
    modal.set_end_date("01.01.2026")
    modal.click_extra(modal.create_button2)
    registry.wait_for_forecast_to_appear_in_list(name_forecast)
    registry.select_forecast_by_name(name_forecast)
    fluid_page = FluidModelTab(authenticated_driver)
    # Открываем вкладку "Модель флюида"
    registry.click_extra(fluid_page.fluid_model_tab)
    fluid_page.click_extra(fluid_page.zonal_model)
    # Создаём флюид
    fluid_page.click_extra(fluid_page.create_button)
    fluid_modal = CreateFluidModelModal(filled_form.driver)
    fluid_modal.wait_until_visible(fluid_modal.modal)

    # Имя и тип флюида
    name_f = BasePage.generate_random_name("Флюид")
    type_f = "Газовая"  # пример, можно параметризовать

    fluid_modal.set_text_input(fluid_modal.name_field, name_f)
    fluid_modal.select_from_combobox(fluid_modal.type_fluid, type_f, fluid_modal.options_from_dropdown)

    # Проверяем единицы измерения давления и температуры
    if fluid_modal.get_input_value(fluid_modal.pressure_unit_dropdown) != "Ат":
        fluid_modal.select_from_combobox(fluid_modal.pressure_unit_dropdown, "Ат", fluid_modal.pressure_unit_options)

    if fluid_modal.get_input_value(fluid_modal.temperature_unit_dropdown) != "C":
        fluid_modal.select_from_combobox(fluid_modal.temperature_unit_dropdown, "C", fluid_modal.temperature_unit_options)

    # Поля давления, температуры и плотности
    pressure_f = "123"
    temperature_f = "200"
    density_f = "0.9"

    fluid_modal.type(fluid_modal.pressure_field, pressure_f)
    fluid_modal.type(fluid_modal.temperature_field, temperature_f)
    fluid_modal.type(fluid_modal.density_gas_field, density_f)

    # Коэффициенты конденсата
    coef_a, coef_b, coef_c, coef_d = "1.1", "2.2", "3.3", "4.4"
    fluid_modal.edit_grid_cell(fluid_modal.сondensation_coefficient_A, coef_a)
    fluid_modal.edit_grid_cell(fluid_modal.сondensation_coefficient_B, coef_b)
    fluid_modal.edit_grid_cell(fluid_modal.сondensation_coefficient_C, coef_c)
    fluid_modal.edit_grid_cell(fluid_modal.сondensation_coefficient_D, coef_d)

    # Сохраняем флюид
    fluid_modal.click_extra(fluid_modal.create_button3)
    fluid_model_page = FluidModelTab(filled_form.driver)
    fluid_model_page.wait_for_fluid_present("#fluidModelGrid", name_f, timeout=10)

    # ---------- Вторая версия прогноза ----------
    filled_form.click_create_button()
    modal2 = CreateForecastVersionModal(filled_form.driver)
    modal2.wait_until_modal_visible()

    name_forecast_2 = BasePage.generate_random_name()
    modal2.set_text_input(modal2.name_input, name_forecast_2)
    modal2.set_start_date("01.01.2025")
    modal2.set_end_date("01.01.2026")
    modal2.click_extra(modal2.create_button2)
    registry.wait_for_forecast_to_appear_in_list(name_forecast_2)
    registry.select_forecast_by_name(name_forecast_2)

    # Открываем вкладку "Модель флюида"
    registry.click_extra(FluidModelTab.fluid_model_tab)

    yield {
        "name_forecast": name_forecast,  #с флидом
        "name_forecast_2": name_forecast_2, # без флюида
        "name_f": name_f,
        "type_f": type_f,
        "pressure_f": pressure_f,
        "temperature_f": temperature_f,
        "density_f": density_f,
        "coef_a": coef_a,
        "coef_b": coef_b,
        "coef_c": coef_c,
        "coef_d": coef_d,
    }

    # ---------- Teardown ----------
    registry.wait_for_forecast_to_appear_in_list(name_forecast_2)
    registry.delete_forecast_by_name(name_forecast_2)

    registry.wait_for_forecast_to_appear_in_list(name_forecast)
    registry.delete_forecast_by_name(name_forecast)
