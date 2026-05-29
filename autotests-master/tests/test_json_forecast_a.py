from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
from pages.base_page import BasePage


correct = 'Файл готов к загрузке. Нажмите кнопку «Создать»'
incorrect = 'Ошибки'

def test_name_field_is_required(reset_forecast_modal):
    """Поле 'Наименование' обязательное.Оставляем пустым Наименование"""
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # Загружаем валидный json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "27.08.json")
    upload_file(modal, file_path)

    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    WebDriverWait(modal.driver, 5).until(lambda d: modal.get_input_value(modal.json_results_field).strip() != "")

    # Проверяем, что кнопка "Создать" НЕ активна
    assert not modal.is_element_enabled(modal.create_button2), "Кнопка 'Создать' активна без заполнения поля 'Наименование'"

def test_results_field_readonly(reset_forecast_modal):
    """Поле 'Результаты проверки' недоступно для редактирования, есть скролл."""
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    results = modal.driver.find_element(*modal.json_results_field)
    assert results.get_attribute("readonly") is not None, "Поле 'Результаты проверки' доступно для редактирования"

def test_check_button_only_for_json(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)
    assert modal.is_element_displayed(modal.check_btn), "Кнопка 'Проверить' не отображается для метода 'Загрузка из JSON'"

def test_check_button_for_other(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()

    # метод "Копирование версии"
    modal.select_from_combobox(modal.creation_method_field, "Копирование версии", modal.creation_method_options)
    assert not modal.is_element_displayed(modal.check_btn), "Кнопка 'Проверить' отображается для метода 'Копирование версии'"

    # метод "Ручной ввод"
    modal.select_from_combobox(modal.creation_method_field, "Ручной ввод", modal.creation_method_options)
    assert not modal.is_element_displayed(modal.check_btn), "Кнопка 'Проверить' отображается для метода 'Ручной ввод'"


def test_create_button_disabled_by_default(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)
    assert not modal.is_element_enabled(modal.create_button2), "Кнопка 'Создать' активна по умолчанию"


 
def test_json_upload_mode_fields_visibility(reset_forecast_modal):
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()

    # Выбираем способ создания
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    json_results_field = modal.wait_until_visible(modal.json_results_field)
    assert json_results_field.is_displayed(), 'Поле "Результат проверки" не появилось при выборе способа "Загрузка из JSON"'

    json_file_input = modal.wait_until_present((By.ID, "jsonFileInput"))
    assert json_file_input is not None, 'Поле "Файл JSON" не появилось'
    
    # Проверяем, что ненужные поля скрыты
    hidden_fields = [
        modal.start_date_field,
        modal.end_date_field,
        modal.calc_step_field,
        modal.report_detail_dropdown,
        modal.description_field
    ]

    for field in hidden_fields:
        assert not modal.is_element_displayed(field), f'Поле {field} не должно отображаться при выборе "Загрузка из JSON"'



def upload_file(modal, file_path, wait_seconds=3): 
    """Универсальная загрузка файла в hidden input (без проверки расширений на бэке)."""
    file_name = os.path.basename(file_path)

    afu_input = modal.wait_until_present(
        (By.CSS_SELECTOR, "app-file-uploader input[type='file'][name='files[]']"),
        timeout=2
    )
    afu_input.send_keys(file_path)

    # Иногда требуется нажать кнопку "загрузить"
    try:
        upload_btn = modal.wait_until_present(
            (By.CSS_SELECTOR, "angular-file-uploader .afu-upload-btn"),
            timeout=2
        )
        upload_btn.click()
        print('ЗАШЕЛ В ТРАЙ')
    except Exception:
        pass

    return file_name

def test_upload_txt_file(reset_forecast_modal):
    """Недопустимый TXT — имя не появляется и кнопка остаётся неактивной."""
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "invalid.txt")
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    # ждём чуть-чуть и проверяем, что label не изменился
    label = modal.driver.find_element(*modal.json_file_label)
    assert 'Выберите файл...' in label.text, f"Файл недопустимого формата отобразился в label: {label.text}"
    assert not modal.is_element_enabled(modal.check_btn), "Кнопка 'Проверить' активировалась для недопустимого формата файла TXT"



def test_upload_json_file(reset_forecast_modal):
    """Корректная загрузка JSON — имя появляется и кнопка активна."""
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "check.json")  # путь к готовому JSON
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = upload_file(modal, file_path)

    # ждём, пока имя появится
    WebDriverWait(modal.driver, 3).until(
        lambda d: file_name in d.find_element(*modal.json_file_label).text
    )
    label = modal.driver.find_element(*modal.json_file_label)
    assert file_name in label.text, f"Имя файла отобразилось некорректно: {label.text}"
    assert modal.is_element_enabled(modal.check_btn), "Кнопка 'Проверить' не активировалась для JSON"

def test_results_field_filled_after_incorrect_check(reset_forecast_modal): # НЕ корректный файл
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)

    # 1. Выбираем метод "Загрузка из JSON"
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "check.json") 
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = upload_file(modal, file_path)

    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    modal.wait.until(lambda d: modal.get_input_value(modal.json_results_field).strip() != "")

    # 4. Проверяем, что поле "Результаты проверки" заполнилось
    results_text = modal.get_input_value(modal.json_results_field).strip()
    print("ИНФА: ", results_text)
    assert results_text != "", "Поле 'Результаты проверки' осталось пустым после нажатия кнопки 'Проверить'"
    lines = results_text.splitlines()
    assert len(lines) > 1, "Ошибки не разделены построчно"
    assert incorrect in results_text, "Поле 'Результаты проверки' не вывел ошибки"
    assert not modal.is_element_enabled(modal.create_button2), "Кнопка 'Создать' активна для некорректного файла"


def test_results_field_filled_after_correct_check(reset_forecast_modal): #корректный файл
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)

    # 1. Выбираем метод "Загрузка из JSON"
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "27.08.json") 
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = upload_file(modal, file_path)
    
    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal.wait_until_clickable(modal.check_btn)
    modal.click_extra(modal.check_btn)
    modal.wait.until(lambda d: modal.get_input_value(modal.json_results_field).strip() != "")

    # 4. Проверяем, что поле "Результаты проверки" заполнилось
    results_text = modal.get_input_value(modal.json_results_field).strip()
    assert  results_text != "", "Поле 'Результаты проверки' осталось пустым после нажатия кнопки 'Проверить'"
    assert correct in results_text, f"Ожидалось {correct}, получено {results_text}"


def test_create_btn_not_enabled(reset_forecast_modal): #корректный файл
    modal = reset_forecast_modal
    modal.wait_until_modal_visible()
    name = BasePage.generate_random_name()
    modal.set_text_input(modal.name_input, name)

    # 1. Выбираем метод "Загрузка из JSON"
    modal.select_from_combobox(modal.creation_method_field, "Загрузка из JSON", modal.creation_method_options)

    # 2. Загружаем json файл
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "27.08.json") 
    assert os.path.exists(file_path), f"Файл {file_path} не найден"

    file_name = upload_file(modal, file_path)
    
    # 3. Ждём, пока кнопка "Проверить" станет активной
    modal.wait_until_clickable(modal.check_btn)
    assert not modal.is_element_enabled(modal.create_button2), "Кнопка 'Создать' активна до проверки файла"

