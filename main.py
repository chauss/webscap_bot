from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from time import sleep, time
from datetime import datetime, timedelta
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from email_client import EmailClient
import traceback

no_result_string = "Derzeit stehen leider keine Termine zur Verfügung."
url = "https://003-iz.impfterminservice.de/impftermine"  # not the real url for public repo
search_button_xpath = "//button[@type='submit']"

notification_email_address = "" # no email for public repo


def wait_for_found_dates(wb):
    headers = wb.find_elements_by_tag_name("h1")
    for h in headers:
        if h.text == "Gefundene Termine":
            return True
    return False


def send_notification():
    try:
        email_client = EmailClient()
        email_client.send_notification(notification_email_address)
        email_client.close()
    except:
        print("Could not send success notification")


def send_alive_notification(tries, failed, exceptions, successes, alive_since, time_alive):
    try:
        email_client = EmailClient()
        email_client.send_alive_notification(notification_email_address, tries, failed, exceptions, successes, alive_since, time_alive)
        email_client.close()
    except:
        print("Could not send alive notification")


def try_to_click_button(b, desired_tries, sleep_time):
    tries = 0
    button_clicked = False

    while tries < desired_tries:
        tries += 1
        try:
            b.click()
            button_clicked = True
            break
        except ElementClickInterceptedException:
            print("Failed to click button in attempt {}".format(tries))
            sleep(sleep_time)
            continue

    if not button_clicked:
        raise ElementClickInterceptedException


def check_if_has_dates():
    print("Initializing web driver...")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    print("Web driver ready!")

    try:
        print("Waiting for page redirect...")
        before_app_route = time()
        WebDriverWait(driver, 240).until(
            ec.presence_of_element_located((By.XPATH, "/html/body/app-root"))
        )
        print("Found app-root in {}s! Looking for visible search button...".format(time() - before_app_route))

        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.XPATH, search_button_xpath))
        )
        print("Search button is visible")

        WebDriverWait(driver, 20).until(
            ec.invisibility_of_element_located((By.XPATH,
                                                "//div[@class='page-loading ets-corona-search-overlay-loading hidden']"))
        )
        print("page-loading element is invisible")

        WebDriverWait(driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, search_button_xpath))
        )
        print("Search button is clickable. Getting search button element...")
        button = WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.XPATH, search_button_xpath))
        )
        print("Got search button! Going to try to click it...")
        try_to_click_button(button, 3, 3)
        print("Button Clicked! Waiting for results...")
        WebDriverWait(driver, 20).until(wait_for_found_dates)

        print("Found result heading! Checking if the \"no_results\" string can be found...")
        found_no_results = False
        no_result_div = WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.XPATH, "//div[@class='ets-search-no-results text-center']"))
        )
        child_divs = no_result_div.find_elements_by_css_selector("div")
        for c_div in child_divs:
            if no_result_string in c_div.text:
                found_no_results = True
                break

        if found_no_results:
            print("Result: There are no appointments yet... :(")
            return False
        else:
            print("Result: There are appointments now! :)")
            return True
    finally:
        print("Closing driver...")
        driver.close()
        driver.quit()


def main_func():
    failed_attempt_sleep_time = 60 * 2
    success_attempt_sleep_time = 60 * 60 * 3
    exception_attempt_sleep_time = 60 * 1
    sleep_time_between_tries = 0
    start_time = datetime.now()

    exception_count = 0
    tries_count = 0
    failed_count = 0
    success_count = 0
    duration_last_try = 0

    while True:
        current_date_time = datetime.now()
        print('\n' + ('#' * 80))
        print("Status:")
        print("Success: {}".format(success_count))
        print("Failed: {}".format(failed_count))
        print("Exceptions: {}".format(exception_count))
        print('-' * 20)
        print("Total Tries: {}".format(tries_count))
        print("Duration last try: {} (hh:mm:ss)".format(timedelta(seconds=duration_last_try)))
        print("Timestamp: {}".format(current_date_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")))
        print('#' * 80)

        print("--- Going to wait {}s before attempting next try".format(sleep_time_between_tries))
        sleep(sleep_time_between_tries)

        if tries_count % 60 == 0:
            send_alive_notification(tries_count, failed_count, exception_count, success_count, start_time,
                                    datetime.now() - start_time)
        tries_count += 1

        time_before = time()
        try:
            has_dates = check_if_has_dates()
            if has_dates:
                print("Found dates! Sending Emails...")
                send_notification()
                sleep_time_between_tries = success_attempt_sleep_time
                success_count += 1
            else:
                print("Did not find dates...")
                sleep_time_between_tries = failed_attempt_sleep_time
                failed_count += 1

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as error:
            sleep_time_between_tries = exception_attempt_sleep_time
            exception_count += 1

            if error.__class__ == TimeoutException:
                print("!!! Timeout Exception appeared !!!")
            else:
                print("An exception appeared:")
                traceback.print_exc()
        finally:
            duration_last_try = time() - time_before


if __name__ == '__main__':
    while True:
        try:
            main_func()
        except KeyboardInterrupt:
            print("Terminating due to KeyboardInterrupt")
            break
        except:
            continue

