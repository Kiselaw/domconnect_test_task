import logging
import os
import signal
import time
from contextlib import suppress

import psutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from constants import (LOGIN_BUTTON, LOGIN_INPUT, PASSWORD_INPUT, PROXY_TAB,
                       PROXY_TABLE_ELEMENTS, SUBMIT_BUTTON)

load_dotenv()

logger: logging.Logger = logging.getLogger("proxy_parser")
console_handler: logging.StreamHandler = logging.StreamHandler()
strfmt: str = "[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s"
datefmt: str = "%Y-%m-%d %H:%M:%S"
formatter: logging.Formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


class ProxyParser:
    def __init__(self) -> None:
        self._driver: webdriver.Chrome = webdriver.Chrome(options=self.options)
        self._driver_pid: int = self._driver.service.process.pid
        self.target_url: str = "https://belurk.online/"
        # По-хорошему все должно быть в .env
        self._login: str = os.getenv("LOGIN", "tzpythondemo@domconnect.ru")
        self._password: str = os.getenv("PASSWORD", "oJanL4dc7g")
        self.logger: logging.Logger = logger

    @property
    def options(self):
        """
        Настройка параметров веб-драйвера
        """
        options: webdriver.ChromeOptions = webdriver.ChromeOptions()
        # драйвер продолжит выполнять действия сразу при загрузке DOM
        options.page_load_strategy = "eager"
        # переводит navigator.webdriver в false
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Отключает плашку "Браузером Chrome управляет автоматизированное ПО"
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        return options

    def run(self) -> None:
        """
        Основной метод, отвечающий за работу скрипта
        """
        try:
            self._driver.get(self.target_url)
            self.login()
            proxy_data: list[str] = self.get_proxy_data()
            self.print_proxy_data(proxy_data)
        except WebDriverException:
            self.logger.debug(
                "Получили ошибку, связанную с работой веб-драйвера:", exc_info=1
            )
        except Exception:
            self.logger.debug("Получили непредвиденную ошибку:", exc_info=1)
        finally:
            self._close_driver()

    def login(self) -> None:
        """Метод для входа в личный кабинет"""
        login_button: WebElement = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, LOGIN_BUTTON))
        )
        login_button.click()
        # Пришлось добавить небольшую задержку, поскольку иначе логин и пароль вводилсь до отработки JS, вследсствие
        # чего поля чистились и пройти аутентификацию не удавалось
        time.sleep(0.5)
        input_login: WebElement = WebDriverWait(self._driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, LOGIN_INPUT))
        )
        input_login.clear()
        input_login.send_keys(os.getenv("LOGIN"))
        input_password: WebElement = WebDriverWait(self._driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, PASSWORD_INPUT))
        )
        input_password.clear()
        input_password.send_keys(os.getenv("PASSWORD"))
        submit_button: WebElement = WebDriverWait(self._driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, SUBMIT_BUTTON))
        )
        submit_button.click()

    def get_proxy_data(self) -> list[str]:
        """Получает необходимую информацию о прокси"""
        proxy_data: list[str] = []
        proxy_tab: WebElement = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, PROXY_TAB))
        )
        proxy_tab.click()
        proxy_table_elements: list[WebElement] = WebDriverWait(self._driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, PROXY_TABLE_ELEMENTS))
        )
        for element in proxy_table_elements:
            data = element.text.split("\n")
            proxy_ip: str = data[4]
            proxy_expiration: str = data[8]
            proxy_data.append(f"{proxy_ip}, {proxy_expiration}")
        return proxy_data

    def print_proxy_data(self, proxy_data: list[str]) -> None:
        """Выводит в консоль полученную информацию о прокси"""
        for proxy in proxy_data:
            self.logger.info(f"{proxy}")

    def _close_driver(self) -> None:
        """Закрывает веб-драйвер"""
        try:
            if not (self._driver and self._driver_pid):
                return
            if self._driver:
                self._driver.quit()
            if self._driver_pid:
                try:
                    parent: psutil.Process = psutil.Process(self._driver_pid)
                except psutil.NoSuchProcess:
                    return
                children: list[psutil.Process] = parent.children(recursive=True)
                for process in children:
                    with suppress(psutil.NoSuchProcess):
                        process.send_signal(signal.SIGTERM)
        except Exception:
            self.logger.warning(
                "Получили ошибку при попытке закрыть драйвер, драйвер возможно не закрыт:",
                exc_info=1,
            )


if __name__ == "__main__":
    parser = ProxyParser()
    parser.run()
