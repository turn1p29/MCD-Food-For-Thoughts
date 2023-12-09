import platform
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def setup_logging():
    logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

def get_chromedriver_path():
    system_platform = platform.system()

    # Driver paths for mac or windows for debugging

    if system_platform == "Windows":
        return 'C:/Users/ernes/Downloads/chromedriver.exe'
    elif system_platform == "Darwin":
        return '/Users/harveywells/Downloads/chromedriver_mac64'
    else:
        raise Exception(f"Unsupported operating system: {system_platform}")

def initialize_webdriver(chromedriver_path):
    chrome_options = webdriver.ChromeOptions()

    #Bypass bot check
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument(f"webdriver.chrome.driver={chromedriver_path}")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    return driver, wait

def open_initial_page(driver, url):
    driver.get(url)

def click_continue_button(driver, wait):
    try:
        continue_button = wait.until(EC.presence_of_element_located((By.ID, "NextButton")))

        if continue_button.is_displayed():
            continue_button.click()
            wait.until(EC.presence_of_element_located((By.ID, "surveyEntryForm")))
            # Enter data into the fields and submit the form as before
    except Exception as e:
        handle_error(e, "Error on initial page")

def input_user_values(driver, user_code, user_spend):
    input_fields = ["CN1", "CN2", "CN3", "AmountSpent1", "AmountSpent2"]

    for field in input_fields:
        element = driver.find_element(By.ID, field)
        if field.startswith("Amount"):
            element.send_keys(str(user_spend[field]))
        else:
            element.send_keys(user_code[field])

    # Submit the form
    submit_button = driver.find_element(By.ID, "NextButton")
    submit_button.click()

def page2_error_check(driver):
    error_checks = [
        ("errorCN2", "Incorrect code error"),
        ("errorAmountSpent2", "Incorrect price error"),
        ("hardblock", "Hard block error")
    ]

    for error_id, log_message in error_checks:
        try:
            error_message = driver.find_element(By.ID, error_id)
            handle_error(f"{log_message}: {error_message.text}", log_message)
        except NoSuchElementException:
            pass
    else:
        # No specific error found, assuming success
        print("Success")

def handle_error(error_message, log_message):
    logging.error(f"{log_message}: {error_message}")
    print(f"{log_message}: {error_message}")

def user_info():
    code = input("Enter the 12 Digit Code: ")
    spend = input("Enter amount spent: ")

    #code = "7Q9DDTFZZWMZ"
    #spend = "1.99"

    user_code = {
        "CN1": code[:4],
        "CN2": code[4:8],
        "CN3": code[8:]
    }

    user_spend = {
        "AmountSpent1": int(spend.split('.')[0]),
        "AmountSpent2": int(spend.split('.')[1])
    }

    return user_code, user_spend

def main():
    setup_logging()
    chromedriver_path = get_chromedriver_path()
    driver, wait = initialize_webdriver(chromedriver_path)

    try:
        open_initial_page(driver, "https://www.mcdfoodforthoughts.com/")
        click_continue_button(driver, wait)

        user_code, user_spend = user_info()
        input_user_values(driver, user_code, user_spend)

        page2_error_check(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
