import os
import time
import pytest
from selenium import webdriver
import chromedriver_binary

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

CLIENT_TEST = "client test"


@pytest.mark.skip(reason=CLIENT_TEST)
def test_add_a_new_page_with_a_graphic():
    # change config before uploading.
    driver = webdriver.Chrome()
    driver.implicitly_wait(4)
    driver.get("http://0.0.0.0:8000/wizard/upload")
    username = driver.find_element_by_name("username")
    username.clear()
    username.send_keys("auto test")
    data_source = driver.find_element_by_name("data_source")
    data_source.clear()
    data_source.send_keys("test_table")

    data_source = driver.find_element_by_name("csvfile")
    full_path = os.path.abspath(
        os.path.join("test_app_deploy_data", "data", "penguin_size", "penguin_size.csv")
    )
    data_source.send_keys(full_path)
    button = driver.find_element_by_xpath('//button[normalize-space()="Submit"]')
    button.click()
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))
    # We use sleep instead of one of the selenium wait methods because we're rely on the flask app itself
    # to restart in debug mode, so it's not a normal web browser interaction
    time.sleep(4)
    driver.get("http://0.0.0.0:8000/wizard/")

    title = driver.find_element_by_name("title")
    title.clear()
    title.send_keys("auto test")

    desc = driver.find_element_by_name("brief_desc")
    desc.clear()
    desc.send_keys("desc test")
    page_name = driver.find_element_by_id("webpage_label_-1")
    page_name.clear()
    page_name.send_keys("new page")
    button = driver.find_element_by_xpath(
        '//button[normalize-space()="Add a Dashboard Panel"]'
    )
    button.click()
    button = driver.find_element_by_xpath('//button[normalize-space()="Add a Graphic"]')
    button.click()
    graphic_title = driver.find_element_by_id("root[title]")
    graphic_title.clear()
    graphic_title.send_keys("auto graphic")

    brief_desc = driver.find_element_by_id("root[brief_desc]")
    brief_desc.clear()
    brief_desc.send_keys("101010101110010101001")

    button = driver.find_element_by_xpath('//button[normalize-space()="Submit"]')
    button.click()
    wait.until(EC.presence_of_element_located((By.ID, "page_0")))

    # so the server can restart (see above comment)
    time.sleep(1)
    driver.get("http://0.0.0.0:8000/dashboard/new_page")
    wait.until(EC.presence_of_element_located((By.ID, "plot_auto_graphic")))
    print("Success")


if __name__ == "__main__":
    test_add_a_new_page_with_a_graphic()
