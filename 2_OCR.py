import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs
import yaml 
import os, json

import functions

###Settings

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
language = settings["language_keys"]
defaultLang = settings["defaultLang"]

###/Settings

#Checks all entries in the bib file with pdfs
def checkLangId(record, fallBackLang):                   
    languages = yaml.load(open(language))   #loads the languages from the yaml file

    try:    #if there is no key = language it will crash otherwise 
        if record["langid"] in languages:        #if the language is in the yaml file
            tempLang = languages[record["langid"]]   #take the proper OCR abreviation for the language
        elif record["langid"] not in languages:      #if not print a warning
            print(record["langid"]+"is not in the "+language+"file, please add. Will try with %s as default" %fallBackLang)
            tempLang = fallBackLang
    except:  #if there is no key = language set tempLang to eng
        tempLang = fallBackLang #default
        
    return tempLang

def processAllFiles(pathToMemex):

    bibData = functions.loadBib(settings["bib_all"])    #loads the bib file
    
    for k,v in bibData.items():        
        lang = checkLangId(v, defaultLang)   
        functions.ocrPublication(pathToMemex, k, lang)

processAllFiles(memexPath)