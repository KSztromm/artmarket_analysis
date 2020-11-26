import os, time
import pandas as pd
from dotenv import load_dotenv
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from artscrap import ArtScrap

############################################

load_dotenv()
start_time = time.time()

local_path = os.environ.get("LOCALPATH")
webdriver_path = os.environ.get("CHROMEPATH")

options = Options()
options.headless = True

driver = webdriver.Chrome(webdriver_path, chrome_options=options)
driver.get('https://artinfo.pl/logowanie')
login=driver.find_element_by_id('user_email')
login.send_keys('tomasz.mrozik0@gmail.com')
pwd=driver.find_element_by_id('user_password')
pwd.send_keys('KlaudiaCud22!')
login_button=driver.find_element_by_xpath("//input[@value='Zaloguj się']")
login_button.click()
driver.implicitly_wait(1)
try:
    last_page = 0
    page = 0

    while last_page == 0:
        page += 1
        print(f'Processing page {page}', end=' ')
        driver.get(f'https://artinfo.pl/wyniki-aukcji?page={page}')
        try:
            next_button = driver.find_element_by_xpath("//span[@class='next']")
            print('...not the last one')
        except:
            last_page = 1
            print('...and this is the last page')

        df = pd.DataFrame(columns=['autor', 'data_aukcji', 'tytul_rok', 'technika', 'rozmiar', 'status', 'cena_wywolawcza', 'cena_sprzedazy', 'nr_dziela'])

        auctions = driver.find_elements_by_xpath("//div[@class='row auction details']")
        for auction in auctions:

            auction_house = auction.find_element_by_xpath("//h2[@class='headings--h2']").get_attribute('innerText')
            print(auction_house)

            df_in = {
                'autor':[],
                'data_aukcji':[],
                'tytul_rok':[],
                'technika':[],
                'rozmiar':[],
                'status':[],
                'cena_wywolawcza':[],
                'cena_sprzedazy':[],
                'nr_aukcji':[],
                'nr_dziela':[]
            }

            
            
            #get_metadata(driver, df_in, 'autor', "//a[@class='auction_list_painter_name']", ".", att='title')

finally:
    driver.quit()

print(f'{time.time()-start_time} seconds')