#Page Object для модального окна создания модели флюида
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CreateFluidModelModal(BasePage):

    # Локаторы модального окна
    modal = (By.CSS_SELECTOR, "modal-container")
    modal_title = (By.XPATH, "//h4[contains(text(), 'Создание флюида')]")
    modal_subtitle = (By.XPATH, "//h4[contains(text(), 'Зонная модель')]")
    # Поля формы
    name_field = (By.XPATH, "//div[contains(@class,'row')][.//label[contains(text(),'Наименование')]]//input")
    type_fluid = (By.XPATH, "//div[contains(@class,'row')][.//label[contains(text(),'Тип флюида')]]//input")

    # поля давления
    pressure_field = (By.XPATH, "//div[contains(@class,'row')][.//label[contains(text(),'Псевдокритическое давление газа')]]//input")
    # Локатор для выпадающего списка единиц измерения давления
    pressure_unit_dropdown = (By.XPATH, "//simpl-apps-select[@id='pressureUnit']//input")
    # Локатор для опций выпадающего списка (когда он открыт)
    pressure_unit_options = (By.CSS_SELECTOR, "div.dropdown-menu.show .dropdown-item")

    # поля температуры
    # Локатор для поля ввода температуры
    temperature_field = (By.XPATH, "//div[contains(@class,'row')][.//label[contains(text(),'Псевдокритическая температура газа')]]//input")
    # Локатор для выпадающего списка единиц измерения температуры
    temperature_unit_dropdown =(By.XPATH, "//label[contains(text(),'температура')]/../following-sibling::div//simpl-apps-select[@id='gasUnit']//input")
    # Локатор для опций выпадающего списка температуры
    temperature_unit_options = (By.CSS_SELECTOR, "div.dropdown-menu.show .dropdown-item")

    # поля плотности
    density_gas_field = (By.XPATH, "//div[contains(@class,'row')][.//label[contains(text(),'Относительная плотность газа по воздуху')]]//input")

    #Коэффициенты вычисления стабильного конденсата
    сondensation_coefficient_A = (By.CSS_SELECTOR, "div[role='gridcell'][col-id='stableA']")
    сondensation_coefficient_B = (By.CSS_SELECTOR, "div[role='gridcell'][col-id='stableB']")
    сondensation_coefficient_C = (By.CSS_SELECTOR, "div[role='gridcell'][col-id='stableC']")
    сondensation_coefficient_D = (By.CSS_SELECTOR, "div[role='gridcell'][col-id='stableD']")
    
    options_from_dropdown = (By.XPATH, "//bs-dropdown-container//virtual-scroller//div[2]/li")
    # Кнопки внутри модалки
    create_button3 = (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[normalize-space()='Создать']")
    cancel_button = (By.XPATH, "//button[contains(text(), 'Отмена')]")
    close_button = (By.CSS_SELECTOR, "button.close")
    
    # Валидационные сообщения
    required_field_error = (By.CSS_SELECTOR, ".invalid-feedback")
