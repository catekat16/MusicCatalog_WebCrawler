from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import time


def check_master(song_title, index_check=False):
    substrings = ['Master','Mast']
    if not index_check:
        return any([substring.lower() in song_title.lower() for substring in substrings])
    else:
        return max([song_title.lower().find(substring.lower()) for substring in substrings])

if __name__ == "__main__":
    PATH = "/Users/xiaoyanyang/Desktop/chromedriver"
    driver = webdriver.Chrome(PATH)
    driver.get("https://cocatalog.loc.gov/cgi-bin/Pwebrecon.cgi?DB=local&PAGE=first")
    
    song_titles = ["20th Century Boy", "Burn Out", "Glorious Domination (Master)", "More Girls Like You", "Stars in the night"]
    #song_titles = ["Glorious Domination (Master)"]
    
    for i in range(len(song_titles)):
        song_title = song_titles[i]
        if check_master(song_title):
            end_index = check_master(song_title, True)
            song_title = song_title[:end_index-1]
        
        # search_term can be song title + catalog (try different search terms)
        
        search = driver.find_element_by_name("Search_Arg")
        search.clear()
        search.send_keys(song_title + "\n")

        driver.implicitly_wait(0.5)
        
        possibilities_list = []
        
        
        try:
            table = driver.find_elements_by_xpath("//form/table[2]/tbody/tr")
        except:
            table = driver.find_elements_by_xpath("//form/table[2]")
            
        num_cols = len(table[1].text.split(":"))
        #print("number of cols is", num_cols)
        if num_cols == 2: # details page of single search result case
            row_item = table[2].text
            #print("row item is", row_item)
            copy_num = row_item.split(":")[-1].split("/")[-2]
            possibilities_list.append(copy_num) 
            
        else: # more than one search result case
            if not i:
                sel = Select(driver.find_element_by_xpath("//select[@name='CNT']"))
                sel.select_by_value("100")
                driver.implicitly_wait(0.5)
                submit_button = driver.find_element_by_xpath("//form/center[2]/form/table/tbody/tr[2]/td/div/div/table/tbody/tr/td[2]/div/input[2]")
                submit = ActionChains(driver)
                submit.click(submit_button)
                submit.perform()
            
            try:
                table = driver.find_elements_by_xpath("//form/table[2]/tbody/tr")
            except:
                table = driver.find_elements_by_xpath("//form/table[2]")
            num_rows = len(table)
            for i in range(1,num_rows):
                row_item = table[i].text #
                copy_num = row_item.split(".")[-1].split(" ")[-2]
                song_info = row_item
                if (song_title.lower() in song_info.lower()):
                    date = row_item.split(".")[-1].split(" ")[-1]
                    if check_master(song_title) and copy_num[:2] == "SR":
                        # possibilities_list.append((copy_num, date)) 
                        # instead of appending date, in better MVP would click into details page 
                        #     and see whether catalog name is listed in authorship on application and append type of work 
                        possibilities_list.append(copy_num)

                    elif copy_num[:2] == "PA" and copy_num[:3] != "PAu": 
                        possibilities_list.append(copy_num) 
        
        print(song_title)
        print(possibilities_list, "\n")
        
        try:
            search_toggle = driver.find_element_by_xpath("//center[2]/font/a[2]/img")
        except:
            search_toggle = driver.find_element_by_xpath("//center[2]/font/img")
        finally:
            back_tosearch = ActionChains(driver)
            back_tosearch.click(search_toggle)
            back_tosearch.perform()
            
    driver.close()