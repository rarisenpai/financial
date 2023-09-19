import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class MorganStanleySpider(scrapy.Spider):
    name = 'morganstanley'
    start_urls = ['https://advisor.morganstanley.com/search?icid=whmt-dbin-findaf-5624']
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv',
    }
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    def move_and_click(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click().perform()

    def parse(self, response):
        self.driver.get(response.url)
        # Wait for the button to be clickable
        try:
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'SearchBox-submit'))
            )
        except:
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'SearchBar-button'))
            )
        
        # Click the button
        search_button.click()

        while True:
            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                # Wait for the "See More" button to appear and be clickable
                see_more_button = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'Results-seeMore'))
                )

                # Click the button
                self.move_and_click(see_more_button)
                time.sleep(3)
            except:
                break
        time.sleep(10)
        try:cards = self.driver.find_elements(By.CSS_SELECTOR,"li.ResultCard")
        except: cards = self.driver.find_elements(By.CSS_SELECTOR,"li.ResultList-item")
        print(len(cards))
        print(cards)
        for card in cards:
            item = {}
            
            try: item['name'] = card.find_element(By.CLASS_NAME,'ResultCard-nameContainer').text.split('\n')[0]
            except: 
                try:
                    item['name'] = card.find_element(By.CLASS_NAME,'Teaser-title').text.split('\n')[0]
                except: item['name'] = None

            try: item['role'] = card.find_element(By.CLASS_NAME,'ResultCard-title').text
            except:
                try:
                    item['role'] = card.find_element(By.CLASS_NAME,'Teaser-titles').text
                except: item['role'] = None
            
            try: item['website'] = card.find_element(By.CLASS_NAME,'ResultCard-button').get_attribute('href')
            except:
                try: item['website'] = card.find_element(By.CLASS_NAME,'Button--hollow').get_attribute('href')
                except: item['website'] = None
            
            try: item['address'] = card.find_element(By.CLASS_NAME,'ResultCard-address').text
            except:
                try:item['address'] = card.find_element(By.CLASS_NAME,'c-AddressRow').text
                except: item['address'] = None

            try:
                phones = card.find_elements(By.CLASS_NAME,'Phone-label')
                item['direct number'] = phones[0].text if phones else None
                item['branch number'] = phones[1].text if len(phones) > 1 else None
            except: 
                try:
                    phones = card.find_elements(By.CLASS_NAME,'Teaser-phone')
                    item['direct number'] = phones[0].text if phones else None
                    item['branch number'] = phones[1].text if len(phones) > 1 else None
                except:
                    item['direct number'] = None
                    item['branch number'] = None


            try: item['Certifications'] = card.find_element(By.CLASS_NAME,'Teaser-list--starbust').text
            except: 
                try: item['Certifications'] = card.find_element(By.CLASS_NAME,'IconList-list')[0].text
                except: item['Certifications'] = None
            
            try: item['Areas of Focus'] = card.find_element(By.CLASS_NAME,'Teaser-list--clipboard)').text
            except:
                try: item['Areas of Focus'] = card.find_element(By.CLASS_NAME,'IconList-list')[1].text
                except: item['Areas of Focus'] = None


            try: item['Linkedin URL'] = card.find_element(By.CLASS_NAME,'LinkedInLink').get_attribute('href')
            except: item['Linkedin URL'] = None
            
            try: item['facebook'] = card.find_element(By.CLASS_NAME,'FacebookLink').get_attribute('href')
            except: item['facebook'] = None
            
            try: item['twitter'] = card.find_element(By.CLASS_NAME,'TwitterLink').get_attribute('href')
            except: item['twitter'] = None
            yield item

        self.driver.close()
