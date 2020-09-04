import pytest
from selenium import webdriver
import chromedriver_binary

CLIENT_TEST = "client test"


@pytest.mark.skip(reason=CLIENT_TEST)
def test_add_a_new_page_with_a_graphic(test_app_client_sql_backed):
    driver = webdriver.Chrome()

    driver.get("http://127.0.0.1:5000/")
    driver.implicitly_wait(2)
    title = driver.find_element_by_name("title")
    title.clear()
    title.send_keys("auto test")
    desc = driver.find_element_by_name("brief_desc")
    desc.clear()
    desc.send_keys("desc test")
    page_name = driver.find_element_by_name("webpage_label")
    page_name.clear()
    page_name.send_keys("new page")
    button = driver.find_element_by_xpath(
        '//button[normalize-space()="Add a Dashboard Panel"]'
    )
    button.click()
    button = driver.find_element_by_xpath('//button[normalize-space()="Add a Graphic"]')
    button.click()
    driver.implicitly_wait(2)
    button = driver.find_element_by_xpath('//button[normalize-space()="Submit"]')
    button.click()
    driver.implicitly_wait(2)
    assert True
