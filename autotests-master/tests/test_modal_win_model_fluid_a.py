import pytest
from pages.create_fluid_model_modal import CreateFluidModelModal
from selenium.webdriver.common.by import By
import random
import string


# 17 После нажатия кнопки "Создать" открывается модальное окно +
# заблокировав другие элементы на темном фоне
def test_modal_opens_and_blocks_background(create_fluid_modal):
    modal = create_fluid_modal
    assert modal.is_element_displayed(modal.modal), "Модальное окно не открылось"

# 18 Форма имеет название "Создание флюида" +
def test_modal_title(create_fluid_modal):
    modal = create_fluid_modal
    assert modal.get_text(modal.modal_title).strip() == "Создание флюида"

# 19 В подзаголовок выводится модель для которой создается флюид +
def test_subtitle_contains_model_name(create_fluid_modal):
    modal = create_fluid_modal
    subtitle_text = modal.get_text(modal.modal_subtitle)
    assert subtitle_text.strip() == "Зонная модель", "Подзаголовок пустой"


#23.+ У поля 'Псевдокритическое давление газа'  выпадающий список единиц измерения имеет значение по умолчанию 'Ат'
def test_pressure_unit_default_is_at(create_fluid_modal):
    modal = create_fluid_modal
    current_unit = modal.get_input_value(modal.pressure_unit_dropdown).strip()
    assert current_unit == "Ат", f"Ожидалось 'Ат' по умолчанию, но выбрано '{current_unit}'"

#25.+ Поле с выпадающим списком единиц измерения давления не может быть пустым
def test_pressure_unit_dropdown_not_empty(create_fluid_modal):
    modal = create_fluid_modal
    current_unit = modal.get_input_value(modal.pressure_unit_dropdown).strip()
    assert current_unit != "", "Выпадающий список единиц давления не должен быть пустым"

#32.+ У поля 'Псевдокритическая температура газа' выпадающий список единиц измерения имеет значение по умолчанию 'C'
def test_temperature_unit_default_is_c(create_fluid_modal):
    modal = create_fluid_modal
    current_unit = modal.get_input_value(modal.temperature_unit_dropdown).strip()
    assert current_unit == "C", f"Ожидалось 'C' по умолчанию, но выбрано '{current_unit}'"

#25. +Поле с выпадающим списком единиц измерения температуры не может быть пустым
def test_pressure_unit_dropdown_not_empty(create_fluid_modal):
    modal = create_fluid_modal
    current_unit = modal.get_input_value(modal.temperature_unit_dropdown).strip()
    assert current_unit != "", "Выпадающий список единиц температуры не должен быть пустым"

# 22 Допустимы дробные значения до 6 знаков работает +
def test_pressure_field_allows_decimal(create_fluid_modal):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)
    modal.set_text_input(modal.pressure_field, "123.1234567")
    value = modal.get_input_value(modal.pressure_field)
    assert "." in value and len(value.split(".")[1]) <= 6

# 26–30 Доступность всех единиц измерения и диапазонов значений (граничные)+
@pytest.mark.parametrize("unit, expected_range", [
    ("Ат", (0, 1000)),
    ("Атм", (0, 967.84)),
    ("Бар", (0, 968.66)),
    ("Psi", (0, 14223.34)),
    ("Па", (0, 98066500)),
])
def test_pressure_units_and_ranges(create_fluid_modal, unit, expected_range):
    modal = create_fluid_modal
    modal.select_from_combobox(modal.pressure_unit_dropdown, unit, modal.pressure_unit_options)

    modal.clear_field(modal.pressure_field)
    modal.type(modal.pressure_field, str(expected_range[1]))
    value = float(modal.get_input_value(modal.pressure_field).replace(",", "."))
    assert expected_range[0] <= value <= expected_range[1], \
        f"Значение {value} вне диапазона {expected_range} для единицы {unit}"

# 26–30 Доступность всех единиц измерения и диапазонов значений(негативные целые) +
@pytest.mark.parametrize("unit, expected_range", [
    ("Ат", (0, 1000)),
    ("Атм", (0, 967.84)),
    ("Бар", (0, 968.66)),
    ("Psi", (0, 14223.34)),
    ("Па", (0, 98066500)),
])
def test_pressure_field_with_boundaries(create_fluid_modal, unit, expected_range):
    modal = create_fluid_modal
    min_val, max_val = expected_range

    # Выбираем единицу измерения
    modal.select_from_combobox(modal.pressure_unit_dropdown, unit, modal.pressure_unit_options)

    # Проверка граничного максимума (должен сохраниться как есть)
    val = modal.get_truncated_input_value(modal.pressure_field, str(max_val), max_val)
    assert val == pytest.approx(max_val), f"Ожидалось {max_val}, но в поле {val} ({unit})"

    # Проверка выхода за верхнюю границу (например, max+1 → должно обрезаться)
    too_large = str(int(max_val) + 1)
    val = modal.get_truncated_input_value(modal.pressure_field, too_large, max_val)
    assert val <= max_val, f"В поле Псевдокритическое давление газа при вводе {too_large} значение {val} не должно превышать {max_val} ({unit})"

    # Проверка отрицательного (например, -1 → в поле должно быть 1)
    val = modal.get_truncated_input_value(modal.pressure_field, "-1", max_val)
    assert val == 1.0, f"При вводе -1 ожидалось 1, но получили {val} ({unit})"
    assert min_val <= val <= max_val

@pytest.mark.parametrize("unit, expected_range, precision", [
    ("Ат", (0, 1000), 6),
    ("Атм", (0, 967.84), 6),
    ("Бар", (0, 968.66), 6),
    ("Psi", (0, 14223.34), 6),
    ("Па", (0, 98066500), 6),
])
def test_pressure_precision_and_rounding(create_fluid_modal, unit, expected_range, precision):
    """
    Проверка дробной части у поля 'Псевдокритическое давление газа': (негативные дробные) +
    - дробная часть не длиннее precision
    - допускается, что дробная часть сбросилась (например, '300.000000' → '300')
    """
    modal = create_fluid_modal
    modal.select_from_combobox(modal.pressure_unit_dropdown, unit, modal.pressure_unit_options)

    # Формируем число на верхней границе диапазона с дробной частью
    base_value = f"{expected_range[1]:.{precision}f}"  # например "1000.000000"
    attempt_value = base_value[:-1] + "1"              # например "1000.000001"

    value = modal.validate_fraction_or_trimmed(
        modal.pressure_field, attempt_value, expected_range[1], precision
    )

    assert expected_range[0] <= value <= expected_range[1], \
        f"Значение {value} вышло за границы {expected_range} для {unit}"

# 31 Допустимы дробные значения до 2 знаков работает +
def test_temperature_field_allows_decimal(create_fluid_modal):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.temperature_field)
    modal.set_text_input(modal.temperature_field, "123.123")
    value = modal.get_input_value(modal.temperature_field)
    assert "." in value and len(value.split(".")[1]) <= 2

# 33–36 Температура Доступность всех единиц измерения и диапазонов значений (граничные)+
@pytest.mark.parametrize("unit, expected_range", [
    ("C", (-100, 300)),       # Цельсия
    ("F", (-148, 572)),       # Фаренгейта
    ("R", (-80, 240)),        # Реомюра
    ("K", (173.15, 573.15)),  # Кельвина
])
def test_temperature_units_and_ranges(create_fluid_modal, unit, expected_range):
    modal = create_fluid_modal
    modal.select_from_combobox(modal.temperature_unit_dropdown, unit, modal.temperature_unit_options)

    modal.clear_field(modal.temperature_field)
    modal.type(modal.temperature_field, str(expected_range[1]))
    value = float(modal.get_input_value(modal.temperature_field).replace(",", "."))
    assert expected_range[0] <= value <= expected_range[1], \
        f"Значение {value} вне диапазона {expected_range} для единицы {unit}"

@pytest.mark.parametrize("unit, expected_range", [
    ("C", (-100, 300)),       # Цельсия
    ("F", (-148, 572)),       # Фаренгейта
    ("R", (-80, 240)),        # Реомюра
    ("K", (173.15, 573.15)),  # Кельвина
])
def test_temperature_units_and_ranges(create_fluid_modal, unit, expected_range):
    """
    Проверка допустимых диапазонов для поля 'Псевдокритическая температура газа'
    при разных единицах измерения(негативные целые). +
    """
    modal = create_fluid_modal
    min_val, max_val = expected_range
    modal.select_from_combobox(modal.temperature_unit_dropdown, unit, modal.temperature_unit_options)

    # Пытаемся ввести значение выше верхней границы
    upper_input = str(expected_range[1] + 1)
    upper_value = modal.get_truncated_input_value(modal.temperature_field, upper_input, min_val)
    assert expected_range[0] <= upper_value <= expected_range[1], \
        f"Значение {upper_value} вышло за верхнюю границу {expected_range} для {unit}"

    # Пытаемся ввести значение ниже нижней границы
    lower_input = str(expected_range[0] - 1)
    lower_value = modal.get_truncated_input_value(modal.temperature_field, lower_input, max_val)

    # Важно: если диапазон допускает отрицательные числа, проверяем тоже
    assert expected_range[0] <= lower_value <= expected_range[1], \
        f"Значение {lower_value} вышло за нижнюю границу {expected_range} для {unit}"



@pytest.mark.parametrize("unit, expected_range, precision", [
    ("C", (-100, 300), 2),
    ("F", (-148, 572), 2),
    ("R", (-80, 240), 2),
    ("K", (173.15, 573.15), 2),
])
def test_temperature_precision_and_rounding(create_fluid_modal, unit, expected_range, precision):
    """
    Проверка дробной части у поля 'Псевдокритическая температура газа'(негативные дробные): +
    - дробь обрезается до precision знаков
    - либо сбрасывается полностью
    """
    modal = create_fluid_modal
    modal.select_from_combobox(modal.temperature_unit_dropdown, unit, modal.temperature_unit_options)

    base_value = f"{expected_range[1]:.{precision}f}"  # например, "300.00"
    attempt_value = base_value[:-1] + "1"              # "300.01"

    value = modal.validate_fraction_or_trimmed(
        modal.temperature_field, attempt_value, expected_range[1], precision
    )

    assert expected_range[0] <= value <= expected_range[1], \
        f"Значение {value} вышло за границы {expected_range} для {unit}"


def test_density_gas_field_min_value(create_fluid_modal):
    """
    Проверка поля 'Относительная плотность газа по воздуху': + 
    - значение не может быть отрицательным
    - допускается ввод нуля и положительных чисел
    """
    modal = create_fluid_modal

    # Проверяем ввод нуля
    modal.clear_field(modal.density_gas_field)
    modal.type(modal.density_gas_field, "0")
    value_zero = float(modal.get_input_value(modal.density_gas_field).replace(",", "."))
    assert value_zero == 0, "Поле должно принимать значение 0"

    # Проверяем ввод положительного числа
    modal.clear_field(modal.density_gas_field)
    modal.type(modal.density_gas_field, "1.12345")
    value_positive = float(modal.get_input_value(modal.density_gas_field).replace(",", "."))
    assert value_positive == 1.1234, f"Ожидалось 1.234, но в поле {value_positive}"

    # Проверяем ввод положительного числа
    modal.clear_field(modal.density_gas_field)
    modal.type(modal.density_gas_field, "999")
    value_positive = float(modal.get_input_value(modal.density_gas_field).replace(",", "."))
    assert value_positive == 999, f"Ожидалось 999, но в поле {value_positive}"

    # Проверяем ввод дробного числа
    modal.clear_field(modal.density_gas_field)
    modal.type(modal.density_gas_field, "1.12345")
    value_positive = float(modal.get_input_value(modal.density_gas_field).replace(",", "."))
    assert value_positive == 1.1234, f"Ожидалось 1.234, но в поле {value_positive}"

    # Пытаемся ввести отрицательное число
    modal.clear_field(modal.density_gas_field)
    modal.type(modal.density_gas_field, "-1")
    value_after_input = float(modal.get_input_value(modal.density_gas_field).replace(",", "."))
    assert value_after_input >= 0, f"Введено {value_after_input}, но значение должно быть >= 0"



@pytest.mark.parametrize("locator, digits", [
    ("сondensation_coefficient_A", 16),  # столбец A
    ("сondensation_coefficient_B", 15),  # столбец B
    ("сondensation_coefficient_C", 15),  # столбец C
    ("сondensation_coefficient_D", 13),  # столбец D
])
def test_condensation_coefficients_precision(create_fluid_modal, locator, digits):
    """
    Проверка допустимой точности дробных значений в таблице 
    'Коэффициенты вычисления стабильного конденсата'. + 
    """
    modal = create_fluid_modal
    field = getattr(modal, locator)   # получаем локатор по имени атрибута

    # Число с большим количеством знаков после запятой
    test_value = "112." + "8" * (digits + 2)

    modal.remove_and_fill(field, test_value)

    raw_value = modal.get_cell_value(field).replace(",", ".").strip()

    assert "." in raw_value, f"Поле {locator} должно содержать дробную часть"
    fractional_part = raw_value.split(".")[1]

    assert len(fractional_part) == digits, (
        f"Поле {locator} должно допускать максимум {digits} знаков после запятой, "
        f"но сохранено {len(fractional_part)}"
    )



@pytest.mark.parametrize("locator", [
    CreateFluidModelModal.сondensation_coefficient_A,
    CreateFluidModelModal.сondensation_coefficient_B,
    CreateFluidModelModal.сondensation_coefficient_C,
    CreateFluidModelModal.сondensation_coefficient_D,
])
def test_condensation_coefficients_precision(create_fluid_modal, locator):
    """
    Проверка ввода дробных значений в таблице 
    'Коэффициенты вычисления стабильного конденсата'.
    """
    modal = create_fluid_modal
    test_value = "-222.33"

    # Вводим через ag-grid редактор
    modal.edit_grid_cell(locator, test_value)

    # Проверяем отображаемое значение
    raw_value = modal.get_cell_value(locator)

    assert "." in raw_value, f"Поле должно содержать дробную часть"
    assert str(raw_value) == test_value.replace(",", "."), \
        f"Ожидалось {test_value}, но получили {raw_value}"

# Не допустимы спец. символы +
def test_pressure_field_not_allows_symbols(create_fluid_modal):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)
    check_text = "!@#$%^&*(;:)"
    modal.set_text_input(modal.pressure_field, check_text)
    value = modal.get_input_value(modal.pressure_field)
    assert value == "", f'Невалидное значение применилось к полю, ожидалось пустое поле, получили {value}'


# Не допустимы буквы +
@pytest.mark.parametrize("locator", [
    (CreateFluidModelModal.pressure_field), 
    (CreateFluidModelModal.temperature_field), 
    (CreateFluidModelModal.density_gas_field),
])
def test_pressure_field_not_allows_letters(create_fluid_modal, locator):
    modal = create_fluid_modal
    modal.wait_until_visible(locator)
    check_text = "ABабsФ"
    modal.set_text_input(locator, check_text)
    value = modal.get_input_value(modal.pressure_field)
    assert value == "", f'Невалидное значение применилось к полю, ожидалось пустое поле, получили {value}'


# 22 Допустимы дробные значения до 6 знаков работает +
def test_pressure_field_allows_decimal(create_fluid_modal):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)
    check_text = ''.join(random.choices(string.ascii_letters, k=10))
    print(check_text)
    modal.set_text_input(modal.pressure_field, check_text)
    value = modal.get_input_value(modal.pressure_field)
    assert value == "", f'Невалидное значение применилось к полю, ожидалось пустое поле, получили {value}'




def test_sucsessful_create(create_fluid_modal, fluid_model_page):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)
    # Имя и тип флюида
    name_f = fluid_model_page.generate_random_name("Флюид")
    type_f = "Газовая"  # пример, можно параметризовать
    fluid_modal = CreateFluidModelModal(fluid_model_page.driver)
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
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_A, coef_a)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_B, coef_b)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_C, coef_c)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_D, coef_d)

    # Сохраняем флюид
    fluid_modal.click_extra(fluid_modal.create_button3)
    fluid_model_page.wait_for_fluid_present("#fluidModelGrid", name_f, timeout=10)
    assert fluid_model_page.is_fluid_present("#fluidModelGrid", name_f), f"Флюид {name_f} не найден в таблице"

def test_nesessary_name(create_fluid_modal, fluid_model_page):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)

    type_f = "Газовая"  # пример, можно параметризовать
    fluid_modal = CreateFluidModelModal(fluid_model_page.driver)
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
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_A, coef_a)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_B, coef_b)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_C, coef_c)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_D, coef_d)

    
    assert fluid_modal.is_element_disabled(fluid_modal.create_button3), 'Кнопка "Создать" активна при пустом наименовании'


    name_f = '  '
    fluid_modal.type(fluid_modal.name_field, name_f)
    # Сохраняем флюид
    fluid_modal.click_extra(fluid_modal.create_button3)
    try:
        fluid_modal.wait_until_visible(fluid_modal.error_locator)
        error = fluid_modal.find(fluid_modal.error_locator)
    except:
        pass

    check = fluid_modal.is_element_displayed(fluid_modal.error_locator)

    # ---- 3. Проверяем, что окно закрылось и не появилось сообщение об ошибке ----
    assert check, 'Не появилось сообщение об ошибке при создании при модели флюида, хотя не ожидалось'
    
    assert "Должно быть указано имя" in error.text, f'Ожидалось сообщение "Должно быть указано имя", но получили {error.text}'
    if check:
        fluid_modal.close_error_notification(fluid_modal.error_locator)


def test_empty_name(create_fluid_modal, fluid_model_page):
    modal = create_fluid_modal
    modal.wait_until_visible(modal.pressure_field)

    type_f = "Газовая"  # пример, можно параметризовать
    fluid_modal = CreateFluidModelModal(fluid_model_page.driver)
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
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_A, coef_a)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_B, coef_b)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_C, coef_c)
    fluid_modal.edit_grid_cell_via_keys(fluid_modal.сondensation_coefficient_D, coef_d)

    name_f = '  '
    fluid_modal.type(fluid_modal.name_field, name_f)
    # Сохраняем флюид
    fluid_modal.click_extra(fluid_modal.create_button3)
    try:
        fluid_modal.wait_until_visible(fluid_modal.error_locator)
        error = fluid_modal.find(fluid_modal.error_locator)
    except:
        pass

    check = fluid_modal.is_element_displayed(fluid_modal.error_locator)

    # ---- 3. Проверяем, что окно закрылось и не появилось сообщение об ошибке ----
    assert check, 'Не появилось сообщение об ошибке при создании при модели флюида, хотя ожидалось'
    
    assert "Должно быть указано имя" in error.text, f'Ожидалось сообщение "Должно быть указано имя", но получили {error.text}'
    if check:
        fluid_modal.close_error_notification(fluid_modal.error_locator)
    fluid_modal.close_all_modals_if_present()
    assert not fluid_model_page.is_fluid_present("#fluidModelGrid", name_f), f"Флюид {name_f} найден в таблице, хотя не должен"

