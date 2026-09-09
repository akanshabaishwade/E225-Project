import random
from src.automation.human_simulator import HumanSimulator
from commons import get_random_word_or_sentence_faker
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

options = uc.ChromeOptions()
options.add_argument("window-size=1920,1080")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--disable-extensions")
# options.add_argument("--disable-infobars")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-features=VizDisplayCompositor")
# options.add_argument("--disable-features=NetworkService")
# options.add_argument("--disable-features=NetworkServiceInProcess")
# options.add_argument("--disable-features=RendererCodeIntegrity")
# options.add_argument("--disable-features=IsolateOrigins,site-per-process")
# options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating")
# options.add_argument("--disable-features=CrossSiteDocumentBlockingAlways,IsolateOrigins,site-per-process")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--disable-blink-features=AutomationControlled,IsolateOrigins,site-per-process")
# options.add_argument("--disable-blink-features=AutomationControlled,IsolateOrigins,site-per-process,CrossSiteDocumentBlockingAlways")
# options.add_argument("--disable-blink-features=AutomationControlled,IsolateOrigins,site-per-process,CrossSiteDocumentBlockingAlways,CrossSiteDocumentBlockingIfIsolating")
driver = uc.Chrome(options=options)

driver.get("https://www.google.com")

options = ['word', 'name', 'country', 'movie', 'music', 'sports', 'technology', 'News']

delay = max(0.01, min(0.3, random.gauss(0.125, 0.025)))
time.sleep(delay)

human_simulator = HumanSimulator(driver)

query = get_random_word_or_sentence_faker(random.choice(options))

human_simulator.input_search_query(query)

# human_simulator.mouse_click()
breakpoint()

driver.quit()



