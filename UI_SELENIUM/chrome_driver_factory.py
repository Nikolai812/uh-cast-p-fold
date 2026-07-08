import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def create_chrome_driver(
    chrome_driver_path: str,
    download_dir: str,
    headless: bool = False
) -> webdriver.Chrome:
    """
    Creates and returns a configured Chrome WebDriver.

    :param chrome_driver_path: Full path to chromedriver.exe
    :param download_dir: Directory where downloaded files will be saved
    :param headless: Run Chrome in headless mode if True
    :return: Selenium Chrome WebDriver
    """

    chrome_options = Options()

    # Ensure download directory exists
    os.makedirs(download_dir, exist_ok=True)

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)

    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--window-position=-3600,-3600")

    service = Service(chrome_driver_path)

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    return driver
