import random
from selenium.webdriver.common.by import By
from ..logging import logger

class GoogleSearch:

    def __init__(self,driver):
        self.driver = driver

    def get_google(self):
        url = "https://www.google.com"

        logger.info(f"{'-'*10}Hitting Google Url {'-'*10}")

        self.driver.get(url)


    def get_elem_xpaths(self):
        ai_show_more = '//*[@aria-label="Show more AI Overview"]'
        people_ask_for =  '//*[text()="People also ask"]/../../following-sibling::div/div[not(@class)]//*[@data-hveid and @data-ved and count(@*)=2]'
        img_show_more =  "//*[contains(text(),'Show more images')]/ancestor::div[@data-ved][1]"
        read_more = '//*[@aria-label="Show more AI Overview"]'

        return random.choice([ai_show_more,people_ask_for,img_show_more,read_more])


    def show_more(self,element):
        self.driver.find_element(element)


    