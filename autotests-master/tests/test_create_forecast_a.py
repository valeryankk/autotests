import pyperclip
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys


def test_modal_title(reset_forecast_modal):
    modal = reset_forecast_modal
    expected_title = "Создание версии прогноза природного газа"
    actual_title = modal.get_text(modal.title)
    assert actual_title == expected_title, f"Ожидался заголовок '{expected_title}', но получили '{actual_title}'"

def test_name_field_allows_input_and_paste(reset_forecast_modal):
    modal = reset_forecast_modal
    name_field = modal.wait_until_visible(modal.name_input)

    label = modal.wait_until_visible(modal.name_label)
    assert label.is_displayed(), "Лейбл 'Наименование' не отображается"
    # Проверка: поле пустое
    assert name_field.get_attribute("value") == "", "Поле 'Наименование' должно быть пустым по умолчанию"
    # 1. Ручной ввод
    test_text = "ПрямойВвод"
    name_field.send_keys(test_text)
    assert name_field.get_attribute("value") == test_text, "Поле не принимает прямой ввод текста"

    # 2. Вставка текста через горячие клавиши Ctrl+V
    name_field.clear()
    clipboard_text = "ТекстИзБуфера"
    pyperclip.copy(clipboard_text)

    name_field.click()
    name_field.send_keys(Keys.CONTROL, "v")

    modal.wait_until_input_value_is(modal.name_input, clipboard_text)
    assert name_field.get_attribute("value") == clipboard_text, "Поле не принимает вставку через Ctrl+V"

    name_field.clear()

def test_name_field_numbers(reset_forecast_modal):
    modal = reset_forecast_modal
    name_field = modal.wait_until_visible(modal.name_input)

    label = modal.wait_until_visible(modal.name_label)
    assert label.is_displayed(), "Лейбл 'Наименование' не отображается"
    text = '1234567890'
    modal.set_text_input(modal.name_input, text)
    text_after = name_field.get_attribute("value")
    assert text_after == text, 'Ошибка ввода цифр в наименование'


    name_field.clear()

def test_name_field_spesial_symbols(reset_forecast_modal):
    modal = reset_forecast_modal
    name_field = modal.wait_until_visible(modal.name_input)

    label = modal.wait_until_visible(modal.name_label)
    assert label.is_displayed(), "Лейбл 'Наименование' не отображается"
    text = '!@#$%^&*()_+-=[]{};:,./<>?~'
    modal.set_text_input(modal.name_input, text)
    text_after = name_field.get_attribute("value")
    assert text_after == text, 'Ошибка ввода специальных знаков в наименование'

    name_field.clear()

def test_date_fields_presence(reset_forecast_modal):
    modal = reset_forecast_modal

    label = modal.wait_until_visible(modal.start_date_label)
    assert label.is_displayed(), "Лейбл 'Дата начала расчета' не отображается"

    label = modal.wait_until_visible(modal.end_date_label)
    assert label.is_displayed(), "Лейбл 'Дата конца расчета' не отображается"

    assert modal.wait_until_visible(modal.start_date_field), "Поле 'Дата начала расчета' не отображается"
    assert modal.wait_until_visible(modal.end_date_field), "Поле 'Дата конца расчета' не отображается"


import time
def test_creation_method_dropdown_select_sequence(reset_forecast_modal):
    modal = reset_forecast_modal

    expected_sequence = ["Копирование версии", "Загрузка из JSON", "Ручной ввод"]
    
    # Шаг 1: Проверяем, что по умолчанию установлен "Ручной ввод"
    field = modal.wait_until_visible(modal.creation_method_field)
    current_value = field.get_attribute("value")
    assert current_value == "Ручной ввод", f"По умолчанию должно быть 'Ручной ввод', но установлено '{current_value}'"
    
    # Шаг 2: Проходим по списку значений
    for option_to_select in expected_sequence:
        field = modal.wait_until_visible(modal.creation_method_field)
        field.click()

        options = modal.wait_until_visible_all(modal.creation_method_options)

        for option in options:
            if option.text.strip() == option_to_select:
                assert option.is_enabled(), f"Опция '{option_to_select}' должна быть активна"
                time.sleep(0.3)
                option.click()
                break
        else:
            assert False, f"Опция '{option_to_select}' не найдена в списке"

        updated_value = field.get_attribute("value")
        assert updated_value == option_to_select, f"Ожидалось '{option_to_select}', но выбрано '{updated_value}'"


def test_date_fields_format(reset_forecast_modal):
    modal = reset_forecast_modal

    # Вводим неполную дату
    modal.set_start_date("01012000")
    modal.wait_until_input_value_is(modal.start_date_field, "01.01.2000")

    modal.set_end_date("31122050")
    modal.wait_until_input_value_is(modal.end_date_field, "31.12.2050")

    start_date = modal.get_start_date()
    end_date = modal.get_end_date()

    assert start_date == "01.01.2000", f"Дата начала имеет неверный формат: {start_date}"
    assert end_date == "31.12.2050", f"Дата конца имеет неверный формат: {end_date}"

def test_start_date_cannot_be_after_end_date(reset_forecast_modal):
    modal = reset_forecast_modal

    modal.set_start_date("31.12.2025")
    modal.set_end_date("01.01.2025")
    modal.wait_until_input_value_is(modal.end_date_field, "")
    assert modal.get_end_date() == "", "Дата конца не сбросилась при дате начала позже даты конца"

    modal.set_end_date("31.12.2025")
    modal.wait_until_input_value_is(modal.end_date_field, "31.12.2025")

    modal.set_start_date("31.12.2026")
    modal.wait_until_input_value_is(modal.start_date_field, "")
    assert modal.get_start_date() == "", "Дата начала не сбросилась при дате конца раньше даты конца"

def test_date_range_cannot_exceed_100_years(reset_forecast_modal):
    modal = reset_forecast_modal

    end_date = "01.01.2100"

    # дата конца больше чем на 100 лет от начала — валидный ввод
    modal.set_start_date("01.01.2000")
    modal.set_end_date(end_date)
    modal.wait_until_input_value_is(modal.end_date_field, end_date)
    assert modal.get_end_date() == end_date, "Дата конца не установилась корректно"

    # Превышаем лимит на 1 день — ожидаем сброс значения
    modal.set_end_date("02.01.2100")
    modal.wait_until_input_value_is(modal.end_date_field, "")
    assert modal.get_end_date() == "", "Дата конца не сбросилась при превышении лимита в 100 лет"

    # Вводим снова корректную дату
    modal.set_end_date("01.01.2100")
    modal.wait_until_input_value_is(modal.end_date_field, "01.01.2100")
    set_date_correct = modal.get_end_date() == "01.01.2100"

    # Меняем дату начала на такую, что превышает лимит — ожидаем сброс конца
    modal.set_start_date("31.12.1999")
    modal.wait_until_input_value_is(modal.end_date_field, "")

    assert modal.get_end_date() == "" and set_date_correct, "Дата конца не сбросилась при превышении лимита в 100 лет"



def test_calendar_opens_on_field_click(reset_forecast_modal):
    modal = reset_forecast_modal

    modal.click_extra(modal.start_date_field)

    # Проверка, что открылся календарь — можно ждать появления любого видимого календарного блока
    calendar = modal.wait_until_visible(modal.calendar_popup)
    assert calendar.is_displayed(), "Календарь не открылся после клика на поле даты"

def test_calendar_month_switch(reset_forecast_modal): #переключение месяца стрелками
    modal = reset_forecast_modal
    modal.click_extra(modal.start_date_field)

    MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь" ]

    current_month_text = modal.get_selected_month()
    current_index = MONTHS.index(current_month_text)

    # Переключаем на следующий месяц
    modal.click_extra(modal.calendar_right_arrow)
    next_month_text = modal.get_selected_month()

    expected_next = MONTHS[(current_index + 1) % 12]  # переход от Декабрь -> Январь
    assert next_month_text == expected_next, f"Ожидался месяц '{expected_next}', но получил '{next_month_text}'"

    # Возвращаемся назад
    modal.click_extra(modal.calendar_left_arrow)
    back_to_current = modal.get_selected_month()
    assert back_to_current == current_month_text, f"Не удалось вернуться к месяцу '{current_month_text}'"

    # Ещё раз влево (предыдущий месяц)
    modal.click_extra(modal.calendar_left_arrow)
    previous_month_text = modal.get_selected_month()

    expected_previous = MONTHS[(current_index - 1) % 12]
    assert previous_month_text == expected_previous, f"Ожидался месяц '{expected_previous}', но получил '{previous_month_text}'"


def test_select_day_from_calendar(reset_forecast_modal):
    modal = reset_forecast_modal
    day = "15"
    modal.click_extra(modal.start_date_field)  # открываем календарь
    calendar = modal.wait_until_visible(modal.calendar_popup)
    modal.click_extra(modal.calendar_day(day))  # кликаем по 15 числу

    selected_date = modal.get_input_value(modal.start_date_field)
    assert not calendar.is_displayed(), "Календарь не закрылся после выбора даты"
    assert selected_date.startswith("15."), f"Дата в поле должна начинаться с 15, получено: {selected_date}"


def test_calendar_year_switch(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.click_extra(modal.start_date_field)

    current_year = int(modal.get_input_value(modal.calendar_year_input))

    # Кликаем стрелку вперед (увеличиваем год)
    modal.click_year_next()
    new_year = int(modal.get_input_value(modal.calendar_year_input))
    assert new_year == current_year + 1, f"Год не увеличился на 1. Был: {current_year}, стал: {new_year}"

    # Кликаем стрелку назад (возвращаем год назад)
    modal.click_year_previous()
    reverted_year = int(modal.get_input_value(modal.calendar_year_input))
    assert reverted_year == current_year, f"Год не вернулся к исходному. Был: {new_year}, стал: {reverted_year}"

    # Дополнительно: можно проверить, что при клике назад год уменьшится
    modal.click_year_previous()
    prev_year = int(modal.get_input_value(modal.calendar_year_input))
    assert prev_year == current_year - 1, f"Год не уменьшился на 1. Был: {current_year}, стал: {prev_year}"

    day = "17"
    modal.click_extra(modal.calendar_day(day))  # кликаем по 15 числу
    selected_date = modal.get_input_value(modal.start_date_field)
    assert selected_date.endswith(f".{prev_year}"), f"Дата в поле должна заканчиваться на {prev_year}, получено: {selected_date}"


def test_manual_year_input_updates_calendar(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.click_extra(modal.start_date_field)

    year = 2030
    # Вводим вручную новый год
    modal.wait_until_visible(modal.calendar_popup)

    
    year_input_elem = modal.wait_until_visible(modal.calendar_year_input)
    year_input_elem.clear()
    year_input_elem.send_keys(str(year))
    year_input_elem.send_keys(Keys.ENTER)


    updated_year = int(modal.get_input_value(modal.calendar_year_input))
    assert updated_year == year, f"Год в календаре не обновился. Ожидалось: {year}, получено: {updated_year}"

    day = "16"
    modal.click_extra(modal.calendar_day(day))  # кликаем по 15 числу
    selected_date = modal.get_input_value(modal.start_date_field)
    assert selected_date.endswith(f".{updated_year}"), f"Дата в поле должна заканчиваться на {updated_year}, получено: {selected_date}"


def test_calc_step_field_properties(reset_forecast_modal):
    modal = reset_forecast_modal
    
    label = modal.wait_until_visible(modal.calc_step_label)
    assert label.is_displayed(), "Лейбл 'Расчетный шаг' не отображается"

    assert modal.is_element_displayed(modal.calc_step_field), "Поле 'Расчетный шаг' не отображается"

    value = modal.get_field_value(modal.calc_step_field)
    assert value == "1", f"Ожидалось значение по умолчанию '1', но получили '{value}'"

    assert modal.is_field_readonly(modal.calc_step_field), "Поле 'Расчетный шаг' должно быть недоступно для редактирования"


def test_report_detailing_dropdown_properties(reset_forecast_modal):
    modal = reset_forecast_modal

    label = modal.wait_until_visible(modal.report_detail_label)
    assert label.is_displayed(), "Лейбл 'Детализация отчетов' не отображается"

    assert modal.is_element_displayed(modal.report_detail_dropdown), "Поле 'Детализация отчетов' не отображается"

    value = modal.get_field_value(modal.report_detail_dropdown)
    assert value == "Каждый шаг", f"Ожидалось значение по умолчанию 'Каждый шаг', но получили '{value}'"

    assert modal.is_field_readonly(modal.report_detail_dropdown), "Поле 'Детализация отчетов' должно быть недоступно"


def test_calc_step_units_dropdown_properties(reset_forecast_modal):
    modal = reset_forecast_modal

    value = modal.get_field_value(modal.calc_step_units_dropdown)
    assert value == "Месяц", f"Ожидалось значение по умолчанию 'Месяц', но получили '{value}'"

    assert modal.is_field_readonly(modal.calc_step_units_dropdown), "Список 'Единицы измерения' должен быть недоступен"

    assert modal.is_element_displayed(modal.calc_step_units_dropdown), "Выпадающий список единиц измерения отсутствует"


def test_description_field_presence_and_input(reset_forecast_modal):
    modal = reset_forecast_modal

    assert modal.is_element_displayed(modal.description_field), "Поле 'Описание' не отображается в форме"

    test_text = "Тестовое описание для проверки ввода"
    modal.set_text_input(modal.description_field, test_text)
    actual_text = modal.get_input_value(modal.description_field)

    assert actual_text == test_text, (
        f"Ожидалось, что в поле 'Описание' будет введено '{test_text}', но получили '{actual_text}'"
    )

def test_description_input(reset_forecast_modal):
    modal = reset_forecast_modal
    text = "Тест ввода"

    modal.set_text_input(modal.description_field, text)
    value = modal.get_input_value(modal.description_field)

    assert value == text, f"Ожидалось '{text}', но получили '{value}'"


def test_lock_edit_checkbox_behavior(reset_forecast_modal):
    modal = reset_forecast_modal
    
    assert modal.is_element_displayed(modal.lock_edit_checkbox), "Чекбокс 'Запретить редактирование версии' не отображается"

    # По умолчанию должен быть false
    assert modal.get_attribute(modal.edit_checkbox, "ng-reflect-model", wait_visible=False) == "false", "Чекбокс должен быть снят по умолчанию"

    checkbox = modal.wait_until_visible(modal.lock_edit_checkbox)

    checkbox.click()
    assert  modal.get_attribute(modal.edit_checkbox, "ng-reflect-model", wait_visible=False) == "true", "Чекбокс должен быть отмечен после клика"

    checkbox.click()
    assert  modal.get_attribute(modal.edit_checkbox, "ng-reflect-model", wait_visible=False) == "false", "Чекбокс должен быть снят после повторного клика"  
