import os, time
import pandas as pd
from dotenv import load_dotenv
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


class ArtScrap:
    """Set of methods used to get data from ArtMarket websites"""
    def __init__(self, driver, output):
        self.driver = driver
        self.output = output


    def get(self, url):
        self.driver.get(url)


    def get_metadata(self, column_name, xpath_general, xpath_detailed, att='innerText', start=0, step=1):
        """Get specific value of all elements with same xpath on a given page"""
        elements = self.driver.find_elements_by_xpath(xpath_general)

        for i in range(start, len(elements), step):
            data = elements[i].find_element_by_xpath(xpath_detailed).get_attribute(att)

            self.output[column_name].append(data)


    def apply_multiple_pages(url, func, args, kwargs):
        """Walks through all existing pages of a given website location"""
        last_page = 0
        page = 0
        self.driver.get(url)

        while last_page == 0:
            page += 1
            func(*args, **kwargs)


############################################

load_dotenv()
start_time = time.time()

local_path = os.environ.get("LOCALPATH")
webdriver_path = os.environ.get("CHROMEPATH")

options = Options()
options.headless = True

driver = webdriver.Chrome(webdriver_path, chrome_options=options)

try:
    pages = range(1,508)
    chunksize = 10
    stamp = 1
    
    for chunk in (pages[pos:pos + chunksize] for pos in range(0, len(pages), chunksize)):

        print(f'Processing pages from {stamp*10-9} to {stamp*10}')

        df = pd.DataFrame(columns=['autor', 'data_aukcji', 'tytul_rok', 'technika', 'rozmiar', 'status', 'cena_wywolawcza', 'cena_sprzedazy', 'nr_dziela'])

        for page in chunk:

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

            driver.get(f'https://sztuka.agraart.pl/search/0/brak/wszystkie/0/0/wszystkie/data-aukcji/malejaco/50/{page}')
            
            get_metadata(driver, df_in, 'autor', "//a[@class='auction_list_painter_name']", ".", att='title')

            get_metadata(driver, df_in, 'data_aukcji', "//div[@class='col-lg-7 nr_kat_list ']", "./span")

            get_metadata(driver, df_in, 'tytul_rok', "//div[@class='object_item_info_name']", ".")

            get_metadata(driver, df_in, 'technika', "//div[@class='object_item_info_technique']", ".", start=0, step=2)

            get_metadata(driver, df_in, 'rozmiar', "//div[@class='object_item_info_technique']", ".", start=1, step=2)

            get_metadata(driver, df_in, 'nr_aukcji', "//div[@class='list-item item-view']", ".", att='data-id-auctionauction')

            get_metadata(driver, df_in, 'nr_dziela', "//div[@class='list-item item-view']", ".", att='data-id-pieceofart')
            

            statuses = driver.find_elements_by_xpath("//div[@class='object_item_info_icon auction_icon']")
            for i in range(len(statuses)):

                status = statuses[i].find_element_by_xpath("./div[starts-with(@class,'object_item_upcoming_auction')]//span").get_attribute('innerText')
                df_in['status'].append(status)
                
                # Ceny obrazow sprzedanych na aukcji
                if status=='zarchiwizowany':
                    df_in['cena_wywolawcza'].append(statuses[i].find_element_by_xpath("./div[@data-original-title='Cena wywoławcza']/div[@class='col-xs-6 price_value']").get_attribute('innerText'))
                    df_in['cena_sprzedazy'].append(statuses[i].find_element_by_xpath("./div[@data-original-title='Cena uzyskana']/div[@class='col-xs-6 price_value']/span").get_attribute('innerText'))   
                
                # Ceny obrazow niesprzedanych - tkwiacych w galerii
                else:
                    dzielo = df_in['nr_dziela'][i]
                    wystapienia = len(df[df['nr_dziela'] == dzielo])

                    driver.get(f"https://sztuka.agraart.pl/licytacja/{df_in['nr_aukcji'][i]}/{dzielo}")
                    ile_aukcji = len(driver.find_elements_by_xpath(f"//table[@id='auctionResults{dzielo}']/tbody/tr"))
                    
                    if (ile_aukcji-wystapienia)>=1:
                        cena_wyw = driver.find_element_by_xpath(f"//table[@id='auctionResults{dzielo}']/tbody/tr[{ile_aukcji-wystapienia}]/td[3]").get_attribute('innerHTML')
                    
                    else:
                        cena_wyw='duplicate'
                    
                    df_in['cena_wywolawcza'].append(cena_wyw)
                    df_in['cena_sprzedazy'].append('None')
                    driver.back()
                    statuses = driver.find_elements_by_xpath("//div[@class='object_item_info_icon auction_icon']")


            del df_in['nr_aukcji']
            
            df_tmp = pd.DataFrame.from_dict(df_in)
            df = df.append(df_tmp, ignore_index=True)
            df = df.drop_duplicates(subset=['data_aukcji', 'nr_dziela'], keep='first')

        df.to_csv(os.path.join(local_path, 'data', str(stamp)+'.csv'), index=False)
        stamp += 1

finally:
    driver.quit()

print(f'{time.time()-start_time} seconds')