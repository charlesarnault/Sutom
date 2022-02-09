#Selenium imports here
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#Other imports here
import time
import numpy as np
import pandas as pd
import re
import os
import wget
import unicodedata
from bs4 import BeautifulSoup as bs

def nth_row_selenium_info(sutom_driver, n) :
    grid = sutom_driver.find_elements(By.CSS_SELECTOR, "div[id='grille']")[0]
    row = grid.find_elements(By.CSS_SELECTOR, "tr")[n]
    letters = row.find_elements(By.CSS_SELECTOR, "td")
    return letters

def nth_row_letters(sutom_driver, n):
    return [(elem.text, elem.get_attribute('class')) for elem in nth_row_selenium_info(sutom_driver, n)]

def selenium_row_to_list(selenium_row):
    return [(elem.text, elem.get_attribute('class')) for elem in selenium_row]

def number_of_letters(letters_list):
    return len(letters_list)

def beginning_list(letters_list):
    beginning = []
    for elem in letters_list:
        if elem[0] != ".":
            beginning.append(elem[0])
        else:
            return beginning

def ending_list(letters_list):
    ending = []
    for elem in reversed(letters_list):
        if elem[0] != ".":
            ending.append(elem[0])
        else:
            return ending

def add_included_letters(letters_list, included_letters):
    for elem in letters_list:
        if elem[1] == "mal-place resultat" or elem[1] == "bien-place resultat":
            included_letters.append(elem[0])
    return list(dict.fromkeys(included_letters))

def add_excluded_letters(letters_list, excluded_letters, included_letters):
    for elem in letters_list:
        if elem[1] == "non-trouve resultat":
            if elem[0] not in included_letters:
                excluded_letters.append(elem[0])
    return list(dict.fromkeys(excluded_letters))

def letters_list_to_url_block(letters_list, included_letters_list, excluded_letters_list):
    beginning_str = ''.join(beginning_list(letters_list)).lower()
    ending_str = ''.join(ending_list(letters_list)).lower()
    url_block = beginning_str + "*" + ending_str
    #Si on connaît des lettres à inclure
    if len(included_letters_list) != 0 :
        included_block = "+".join([letter.lower() for letter in included_letters_list])
        url_block = url_block + "/" + included_block
    #Si on connaît des lettres à exclure
    if len(excluded_letters_list) != 0 :
        excluded_block = "/-" + "-".join([letter.lower() for letter in excluded_letters_list])
        url_block = url_block + excluded_block
    url_block = url_block + "/" + str(number_of_letters(letters_list))
    return url_block

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def choosing_best_word(sutom_driver, words_list, nb_of_tries):

    candidate_number = 0

    #On parcourt la liste de candidats et ont test chaque mot
    for candidate in words_list:

        return_candidate = True

        while return_candidate :

            #On le confronte à chaque essai réalisé
            for try_index in range(nb_of_tries):

                letters_list = nth_row_letters(sutom_driver, try_index)

                #On sait que les lettres exclues sont bien exclues
                #On sait aussi que les lettres rouges et jaunes sont bien dans le mot
                #On doit donc simplement tester les positions (rouges en place, jaunes bougées)

                for letter_index in range(len(letters_list)) :

                    elem = letters_list[letter_index]

                    #On commence par vérifier qu'on est RAS pour toutes les lettres rouges
                    if elem[1] == "bien-place resultat":
                        if elem[0] != candidate[letter_index]:
                            return_candidate = False
                            break

                    #On vérifie ensuite que les lettres jaunes ne sont pas à la même place que précédemment mais qu'elles sont bien présentes
                    elif elem[1] == "mal-place resultat":
                        if elem[0] == candidate[letter_index]:
                            return_candidate = False
                            break
                        elif elem[0] not in candidate:
                            return_candidate = False
                            break

            if return_candidate :
                #print("Il a fallu chercher le mot n° " + str(candidate_number))
                return candidate

        candidate_number += 1

def submitting_candidate(sutom_driver, word) :
    for char in word:
        element = sutom_driver.find_element_by_xpath(
            f"//div[@data-lettre='{char}']")
        element.click()
    sutom_driver.find_element_by_xpath(f"//div[@data-lettre='_entree']").click()

def finished_test(row) :
    for letter in row:
        if letter[1] != "bien-place resultat":
            return False
    return True

def motsavec_cookies_closing_button(cookies_list) :
    for index in range(len(cookies_list)):
        if cookies_list[index].text == "continuer sans accepter" :
            return index
