from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pytest
from conftest import load_invalid_login_data

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages.login_page import LoginPage


# ------------------------------------------------------ НАЛИЧИЕ ПОЛЕЙ ------------------------------------------------------
def test_username_field_displayed(driver, base_url, login_url):
    page = LoginPage(driver, base_url, login_url)
    page.open()
    assert page.is_element_displayed(page.username_input)

def test_password_field_displayed(driver, base_url, login_url):
    page = LoginPage(driver, base_url, login_url)
    page.open()
    assert page.is_element_displayed(page.password_input)

def test_signin_button_displayed_and_enabled(driver, base_url, login_url):
    page = LoginPage(driver, base_url, login_url)
    page.open()
    assert page.is_element_displayed(page.signin_button)
    assert page.is_button_enabled()


# ------------------------------------------------------ ЧЕКБОКС ------------------------------------------------------
def test_remember_me_toggle(driver, base_url, login_url):
    page = LoginPage(driver, base_url, login_url)
    page.open()

    # 1. Чекбокс отображается и по умолчанию не выбран
    assert page.is_element_displayed(page.remember_me_checkbox)
    assert not page.is_remember_me_selected()

    # 2. Кликаем — он должен стать выбранным
    page.click_remember_me()
    assert page.is_remember_me_selected()

    # 3. Кликаем снова — он должен стать невыбранным
    page.click_remember_me()
    assert not page.is_remember_me_selected()

# ------------------------------------------------------ ВАЛИДАЦИЯ ВВОДА ------------------------------------------------------


def test_valid_login(driver, base_url, login_url, credentials):
    page = LoginPage(driver, base_url, login_url)
    page.open()

    page.login(credentials["username"], credentials["password"])

    WebDriverWait(driver, 10).until(lambda d: "X" in d.title)

    assert "X" in driver.title
    assert driver.current_url.startswith(f"{page.base_url}/X")


# невалидные данные
@pytest.mark.parametrize("case", load_invalid_login_data())
def test_invalid_login(driver, base_url, login_url, case):
    page = LoginPage(driver, base_url, login_url)
    page.open()
    page.login(case["username"], case["password"])

    assert page.get_error_text() == "Invalid username or password.", f"Провал на данных: {case}"

# ------------------------------------------------------ ПОВТОРНЫЙ ВВОД ------------------------------------------------------

def test_partial_clear_and_continue_typing(driver, base_url, login_url):
    page = LoginPage(driver, base_url, login_url)
    page.open()

    # Вводим начальное значение
    page.append_to_username("testuser")
    page.append_to_password("secret123")

    # Частично стираем и дописываем
    page.append_to_username(Keys.BACKSPACE * 4 + "name")   # удалит 'user' → 'test' + 'name' → 'testname'
    page.append_to_password(Keys.BACKSPACE * 3 + "456")    # удалит '123' → 'secret' + '456' → 'secret456'


    # Получаем поля напрямую
    username_field = driver.find_element(*page.username_input)
    password_field = driver.find_element(*page.password_input)

    # Проверяем итоговые значения
    assert username_field.get_attribute("value") == "testname"
    assert password_field.get_attribute("value") == "secret456"

