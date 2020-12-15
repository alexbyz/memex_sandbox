import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs
import yaml 
import os, json

import functions
import huber_interface_functions

###Settings

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
language = settings["language_keys"]
defaultLang = settings["defaultLang"]

def createIndex(pathToMemex):

    bibData = functions.loadBib(settings["bib_all"])

    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    complete =""

    for k,v in bibData.items():         
        path = functions.generatePublPath(memexPath, k)     
    	
        entry = "<li><a href="+"@PATHTOPUBL@/pages/DETAILS.html"+">[@CITEKEY@]</a> @AUTHOR@ (@DATE@) - <i>@TITLE@</i></li>"

        entry = entry.replace("@PATHTOPUBL@", path)
        entry = entry.replace("@CITEKEY@", k)
        if "author" in v: 
            entry = entry.replace("@AUTHOR@", v["author"].replace("{",""))
        else:
            entry = entry.replace("@AUTHOR@", "MISSING")
        if "date" in v: 
            entry = entry.replace("@DATE@", v["date"])
        else:
            entry = entry.replace("@DATE@", "MISSING")
        if "title" in v: 
            entry = entry.replace("@TITLE@", v["title"].replace("{",""))
        else:
            entry = entry.replace("@TITLE@", "MISSING")
        complete = complete + entry + "\n"
    
    template = template.replace("@MAINCONTENT@", complete)
    
    with open("index.html", "w", encoding="utf8") as f9:
        f9.write(template)

def processAllEntries(pathToMemex):

    bibData = functions.loadBib(settings["bib_all"])    #loads the bib file
    
    for k,v in bibData.items():      
        
        path = functions.generatePublPath(memexPath, k)
        path = path + "\\" + k +".bib" 
        huber_interface_functions.generatePublicationInterface(k, path)    

processAllEntries(memexPath)
createIndex(memexPath)
