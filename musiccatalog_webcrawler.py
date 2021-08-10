from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from collections import defaultdict

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font


def check_master(song_title, index_check=False):
    substrings = ['Master','Mast']
    if not index_check:
        return any([substring.lower() in song_title.lower() for substring in substrings])
    else:
        return max([song_title.lower().find(substring.lower()) for substring in substrings])

def create_output(copyright_dict, name):
    wb =  Workbook()
    ws =  wb.active
    headings = ["#","Song","Registration #"]
    ws.append(headings)
    
    for key in copyright_dict.keys():
        #char = get_column_letter(col)
        # easy mvp but need to store original row number and do something like ws[char + row_iter]
        row_num = key[0]
        song_title = key[1]
        copy_num = copyright_dict[key]
        ws.append([row_num, song_title, copy_num])
    
    wb.save(name + '.xlsx')
    print("Check out the output file!")

if __name__ == "__main__":

    require_cols = [2, 2]
    dataframe1 = pd.read_excel('/Users/xiaoyanyang/Desktop/MusicCatalog_WebCrawler/input_Song_Titles.xlsx', engine = 'openpyxl', usecols = require_cols, skiprows = 2, header = None).head(-142)
    copyright_dict = defaultdict(str)

    song_titles = []
    #breaks_code = ["I'M TOO SEXY", 'HUMBLE AND KIND (TIM MCGRAW MA', 'HOLIDAY (SSH)', "CAN'T YOU SEE (U.S. ONLY AS OF)", "HIGHWAY DON'T CARE (TIM MCGRAW", '25 OR 6 TO 4 (GOARMY REMIX)', 'DANCE HALL DAYS (WANG CHUNG RE', 'SHOTGUN RIDER (TIM MCGRAW MAST', 'SHOTGUN RIDER (TIM MCGRAW MAST', 'BAREFOOT BLUE JEAN NIGHT (BMI']
    breaks_code = ["I'M TOO SEXY", 'LET MY LOVE OPEN THE DOOR', "CAN'T YOU SEE (U.S. ONLY AS OF)", "WON'T GET FOOLED AGAIN", "WON'T GET FOOLED AGAIN", 'LOOK WHAT YOU MADE ME DO']
    
    for index, row in dataframe1.iterrows():
        if row[2].split("-")[1] not in breaks_code:
            if "(" in row[2]:
                first_half = row[2].split("(")[0]
                song_titles.append((first_half.split("-"))[1])
            else:
                song_titles.append((row[2]).split("-")[1])

    PATH = "/Users/xiaoyanyang/Desktop/chromedriver"
    driver = webdriver.Chrome(PATH)
    driver.get("https://cocatalog.loc.gov/cgi-bin/Pwebrecon.cgi?DB=local&PAGE=first")
    
    #song_titles = ["20th Century Boy", "Burn Out", "Glorious Domination (Master)", "More Girls Like You", "Stars in the night"]
    #song_titles = ["Glorious Domination (Master)"]
    #song_titles = ["CAN'T YOU SEE (U.S. ONLY AS OF)"]
    #song_title = ["HUMBLE AND KIND (TIM MCGRAW MA"]

    #if "(" in song_title[0]:
    #    first_half = row[2].split("(")[0]
    #    song_titles.append((first_half.split("-"))[1])

    count = 0
    for i in range(len(song_titles)):
        count += 1
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
            try: 
                copy_num = row_item.split(":")[-1].split("/")[-2]
            except:
                # /html/body/form[1]/table[2]/tbody/tr[3]/th
                # need to figure out how to access the column over (while keeping in mind that registration number can show up in different rows)
                row_index = driver.find_elements_by_xpath("//*[contains(text(), 'Registration Number')]").index
                #print(row_index)
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
        
        print(count)
        print(song_title)
        print(possibilities_list, "\n")

        #{(song name, row num):copyright #} dictionary
        # in the excel file row num offset by +2
        if not possibilities_list:
            copyright_dict[(count, song_title)] = " "
        else:
            copyright_dict[(count, song_title)] = possibilities_list[0]
        
        try:
            search_toggle = driver.find_element_by_xpath("//center[2]/font/a[2]/img")
        except:
            search_toggle = driver.find_element_by_xpath("//center[2]/font/img")
        finally:
            back_tosearch = ActionChains(driver)
            back_tosearch.click(search_toggle)
            back_tosearch.perform()
            
    driver.close()
    print(copyright_dict) 
    
    create_output(copyright_dict, "Registration Numbers")

# next steps: 
# - paste to excel file (just take first element of list)
# - use more complete information of excel sheet (catalog name, artist name, date)
# - figure out how to seek registration number dynamically within details page of song
# turn into object-oriented so that things like copyright_dict are global
# build a web interface, start the process after uploading input file and pressing button 
# fix 20th century boy Master version (don't split at the beginning right away on "(" if detect Master)
# if single word keyword song (Holiday, Body), search on more information
# look up web crawler deepening search techniques / algorithms