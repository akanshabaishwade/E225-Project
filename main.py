import random
from src.automation.human_simulator import HumanSimulator
from commons import get_random_word_or_sentence_faker
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
from src.logging import logger
from src.automation.google_work import GoogleSearch


def random_words():
    logger.info(f"{"-"*10}Searching for 2 Random Words First {"-"*10}")

    for i in range(2):
        options = ['word', 'name', 'country', 'movie', 'music', 'sports', 'technology', 'News']
        query = get_random_word_or_sentence_faker(random.choice(options))
        gs.get_google()

        time.sleep(random.randint(3,5))
        human_simulator.input_search_query(query)
        time.sleep(random.randint(3,5))
        
        for i in range(5):
            elem_xpath = gs.get_elem_xpaths()
            logger.info(f"{"-"*10}Elem Xpath found : {elem_xpath} {"-"*10}")
            try:
                human_simulator.move_to_element_like_human(driver.find_element(By.XPATH,elem_xpath))
                human_simulator.mouse_click(elem_xpath)
                break
            except Exception as e:    
                print(f"{elem_xpath} not found . this is the error : {e}")           

        else:
            raise Exception("Somethings Wrong in here")


if __name__ == "__main__":

    logger.info("Script Has Been Started..............")

    options = uc.ChromeOptions()
    options.add_argument("window-size=1920,1080")
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options,version_main=152)

    gs = GoogleSearch(driver)
    human_simulator = HumanSimulator(driver)

    random_words()

    logger.info(f"{"-"*10} Process Completed {"-"*10}")
    
    driver.quit()