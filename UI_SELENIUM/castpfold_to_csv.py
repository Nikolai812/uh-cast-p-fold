import configparser
import csv
import os
import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def enter_text_in_input(driver, input_id, text):
    """
    Locates an input field by ID and enters the specified text.

    Parameters:
    - input_id: The ID of the input field.
    - text: The text to enter into the input field.
    """
    input_field = driver.find_element(By.ID, input_id)
    input_field.clear()  # Clear any existing text
    input_field.send_keys(text)

def click_button_by_id(driver, button_id):
    """
    Locates a button by ID and clicks it.

    Parameters:
    - button_id: The ID of the button.
    """
    button = driver.find_element(By.ID, button_id)
    button.click()


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DEFAULT']


def write_pocket_info_csv(driver, csv_filename):
    # Locate the table element
    table = driver.find_element(By.CSS_SELECTOR, "table")

    # Extract headers
    headers = []
    header_row = table.find_element(By.CSS_SELECTOR, "thead tr")
    for th in header_row.find_elements(By.TAG_NAME, "th"):
        if th.text.strip():  # Skip empty header cells
            headers.append(th.text.strip())

    # Extract rows
    rows = []
    for tr in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        row = []
        for td in tr.find_elements(By.TAG_NAME, "td"):
            if td.text.strip():  # Skip empty cells

                row.append(td.text.strip())
        if row:  # Only add non-empty rows
            rows.append(row)

    # Write to CSV
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Data written to {csv_filename}")


def open_atom_info_save_csv(driver, output_directory):
    # Locate all rows in the table
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.ant-table-row-level-0")

    for i, row in enumerate(rows):
        try:
            # Get pocket ID from the second column
            pocket_id = row.find_elements(By.TAG_NAME, "td")[1].text.strip()

            # Click the expand icon
            expand_icon = row.find_element(By.CSS_SELECTOR, "td.ant-table-row-expand-icon-cell span.ant-table-row-collapsed")
            expand_icon.click()
            time.sleep(1)  # Wait for the row to expand


            # Click the "Atom Info" element
            atom_info_header = row.find_element(By.XPATH, "./following-sibling::tr//*[contains(text(), 'Atom Info')]")

            atom_info_header.click()
            time.sleep(1)  # Wait for the atom info to load

            # Locate the atom info table
            atom_info_table = row.find_element(By.XPATH, "./following-sibling::tr//div[contains(@class, 'ant-table-content')]//table")
            #row.find_element(By.CSS_SELECTOR, "div.ant-table-content table")

            # Extract headers
            headers = []
            header_row = atom_info_table.find_element(By.CSS_SELECTOR, "thead tr")
            for th in header_row.find_elements(By.TAG_NAME, "th"):
                if th.text.strip():
                    headers.append(th.text.strip())

            # Extract rows
            atom_rows = []
            for tr in atom_info_table.find_elements(By.CSS_SELECTOR, "tbody tr"):
                atom_row = []
                for td in tr.find_elements(By.TAG_NAME, "td"):
                    if td.text.strip():
                        atom_row.append(td.text.strip())
                if atom_row:
                    atom_rows.append(atom_row)

            # Write to CSV
            with open(f"{output_directory}/pocket_{pocket_id}_atom_info.csv", 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(atom_rows)

            print(f"Atom info for pocket {pocket_id} saved to pocket_{pocket_id}_atom_info.csv")

            # Close the "Atom Info" section
            atom_info_header.click()
            time.sleep(0.5)

            # Collapse the row
            expand_icon = row.find_element(By.CSS_SELECTOR, "td.ant-table-row-expand-icon-cell span.ant-table-row-expanded")
            expand_icon.click()
            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing pocket {i}: {e}")
            continue




if __name__ == '__main__':
    # Load config
    config = load_config()
    chrome_driver_path = config['chrome_driver_path']
    base_url = config['base_url']
    job_number = config['job_number']
    output_directory   = config['out_dir'] + '_' + job_number


    # Set up Chrome options to automatically download files
    chrome_options = Options()
    download_dir = r"C:\Windriver"
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Set up the WebDriver with the specified path
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the specified URL
        driver.get(f"{base_url}?{job_number}")
        time.sleep(3)
        write_pocket_info_csv(driver, f"{output_directory}/pocket_info.csv")
        open_atom_info_save_csv(driver, output_directory)
    except BaseException as e:
        print("While running: ", e)
    finally:
        print("this is finally, going to quit driver")
        driver.quit()
        print("after quit")
