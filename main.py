#Selenium imports here
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#Other imports here
import utils as ut
import time
import numpy as np
import pandas as pd
import re
import os
import wget
import unicodedata
from bs4 import BeautifulSoup as bs

#Sutom Driver

#Initialisation des variables utiles
number_of_tries = 0
included_letters = []
excluded_letters = []
beginning = []
ending = []
finished = False

sutom_url = "https://sutom.nocle.fr/"
option = webdriver.ChromeOptions()
#option.add_argument('--headless')
serv = Service(ChromeDriverManager().install())
sutom_driver = webdriver.Chrome(service = serv, options = option)
sutom_driver.get(sutom_url)

rules_close_button = sutom_driver.find_elements(By.CSS_SELECTOR, "a[id='panel-fenetre-bouton-fermeture']")[0]
try:
    rules_close_button.click()
except:
    pass

for number_of_games in range(6):

    if finished == True:
        break

    new_row = ut.nth_row_letters(sutom_driver, number_of_games)

    url_block = ut.letters_list_to_url_block(new_row, included_letters, excluded_letters)
    motsavec_url = "https://motsavec.fr/" + url_block + "-lettres/dictionnaire/mots-courants"

    #MotsAvec driver
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    serv = Service(ChromeDriverManager().install())
    motsavec_driver = webdriver.Chrome(service = serv, options = option)
    motsavec_driver.get(motsavec_url)

    #Cookies pop-up closing
    motsavec_cookies_popup = motsavec_driver.find_elements(By.CSS_SELECTOR, "button[class='sd-cmp-JnaLO']")
    try:
        button_index = ut.motsavec_cookies_closing_button(cookies)
        motsavec_cookies_popup[button_index].click()
    except:
        pass

    #MotsAvec scraping
    words_list = []
    selenium_words_list_wrapped = motsavec_driver.find_elements(By.CSS_SELECTOR, "ul[class='inline-list words group0 sortcount']")[0]
    selenium_words_list = selenium_words_list_wrapped.find_elements(By.CSS_SELECTOR, "li")
    for elem in selenium_words_list:
        corrected_word = ut.remove_accents(elem.text.upper())
        words_list.append(corrected_word)

    #Candidate picking
    candidat_retenu = ut.choosing_best_word(sutom_driver, words_list, number_of_games + 1)

    #Candidate submitting
    ut.submitting_candidate(sutom_driver, candidat_retenu)

    time.sleep(3)

    prev_row = ut.nth_row_letters(sutom_driver, number_of_games)

    incldued_letters = ut.add_included_letters(prev_row, included_letters)
    excluded_letters = ut.add_excluded_letters(prev_row, excluded_letters)

    finished = ut.finished_test(prev_row)

game_summary = sutom_driver.find_elements(By.CSS_SELECTOR, "pre[id='fin-de-partie-panel-resume']")[0].text
