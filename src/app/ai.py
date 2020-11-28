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
ai_login = os.environ.get("AILOGIN")
ai_pwd = os.environ.get("AIPWD")

options = Options()
options.headless = True

driver = webdriver.Chrome(webdriver_path, chrome_options=options)
driver.get('https://artinfo.pl/logowanie')
login=driver.find_element_by_id('user_email')
login.send_keys(ai_login)
pwd=driver.find_element_by_id('user_password')
pwd.send_keys(ai_pwd)
login_button=driver.find_element_by_xpath("//input[@value='Zaloguj się']")
login_button.click()
driver.implicitly_wait(10)
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

        auctions = driver.find_elements_by_xpath("//div[@class='row auction details']//div[@class='row justify-content-between auction__actions no-gutters']")
        print(f'Aukcji na stronie: {len(auctions)}')
        for i in range(len(auctions)):
            print(i)
            if auctions[i].find_element_by_xpath(".//span").get_attribute('innerText') == "Zobacz wyniki":
                button_wyniki = auctions[i].find_element_by_xpath(".//a").click()
                time.sleep(1) #important for button load
                driver.find_element_by_xpath("//button[@class='all-records']").click()
                time.sleep(1)
                painters = driver.find_elements_by_xpath("//div[starts-with(@id, 'artwork_')]")
                print(len(painters))
                for j in range(len(painters)):
                    print(painters[j].find_element_by_xpath(".//span[@class='artist-name']").get_attribute('innerText'))

                driver.back()
                driver.back()
                auctions = driver.find_elements_by_xpath("//div[@class='row auction details']//div[@class='row justify-content-between auction__actions no-gutters']")

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
            else:
                print('Brak uprawnien dla tej aukcji')
                
                
                #get_metadata(driver, df_in, 'autor', "//a[@class='auction_list_painter_name']", ".", att='title')

finally:
    driver.quit()

print(f'{time.time()-start_time} seconds')