# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions    #imports our functions 

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml"       #settings
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
langKeys = yaml.load(open(settings["language_keys"]))

###########################################################
# TRICKY FUNCTIONS ########################################
###########################################################

# the function creates a temporary copy of a PDF file
# with comments and highlights removed from it; it creates
# a clean copy of a PDF suitable for OCR-nig 
def removeCommentsFromPDF(pathToPdf):
    with open(pathToPdf, 'rb') as pdf_obj:      #opens file
        pdf = PyPDF2.PdfFileReader(pdf_obj)     #saves contend of the opened file
        out = PyPDF2.PdfFileWriter()            #destination for the data
        for page in pdf.pages:                  #loops through the lines
            out.addPage(page)                   #adds page after page
            out.removeLinks()                   #and replaces the stuff we dont want
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf")       #new path - so we dont lose our comments
        with open(tempPDF, 'wb') as f:          #writes a ned cleand up pdf with _temp as name
            out.write(f)
    return(tempPDF)

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language):
    # generate and create necessary paths
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # generate CLEAN pdf (necessary if you added highlights and comments to your PDFs)
    pdfFileTemp = removeCommentsFromPDF(pdfFile)

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}        #new empty dictionary
        images = pdf2image.convert_from_path(pdfFileTemp)   #makes images from of pdf
        pageTotal = len(images)     #gets page count
        pageCount = 1                  #counting variable
        for image in images:            #loops through all the images
            image = image.convert('1') # binarizes image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)    #path for the new image
            image.save(finalPath, optimize=True, quality=10)    #saves image with the count number as name

            text = pytesseract.image_to_string(image, lang=language)    #gets the language in the image
            textResults["%04d" % pageCount] = text  #saves the text in the dictionary, with the pagenumber as key

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1  #counts up

        with open(jsonFile, 'w', encoding='utf8') as f9:
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)    #dumps the dictionary into a json file
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)      #if a json file exists --> it has been ocred allready

    os.remove(pdfFileTemp)  #no more use for the temp pdf

def identifyLanguage(bibRecDict, fallBackLanguage):     #gets the rigth language for the ocr
    if "langid" in bibRecDict:                          #language is saved in the bib file, usually
        try:
            language = langKeys[bibRecDict["langid"]]    #checks for entry
            message = "\t>> Language has been successfuly identified: %s" % language
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage
            language = fallBackLanguage     #if not, use a default language, and print a warning
    else:
        message = "\t>> No data on the language of the publication"     #is there no langid?
        message += "\t>> For now, trying `%s`..." % fallBackLanguage    #again, default language
        language = fallBackLanguage
    print(message)
    return(language)

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#ocrPublication("AbdurasulovMaking2020", "eng")

###########################################################
# PROCESS ALL RECORDS: APPROACH 1 #########################
###########################################################

"""
def processAllRecords(bibData):
    for k,v in bibData.items():
        # 1. create folders, copy files
        functions.processBibRecord(memexPath, v)
        # 2. OCR the file
        language = identifyLanguage(v, "eng")
        ocrPublication(memexPath, v["rCite"], language)
bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)
"""

###########################################################
# PROCESS ALL RECORDS: APPROACH 2 #########################
###########################################################

# Why this way? Our computers are now quite powerful; they
# often have multiple cores and we can take advantage of this;
# if we process our data in the manner coded below --- we shuffle
# our publications and process them in random order --- we can
# run multiple instances fo the same script and data will
# be produced in parallel. You can run as many instances as
# your machine allows (you need to check how many cores
# your machine has). Even running two scripts will cut
# processing time roughly in half.

def processAllRecords(bibData):
    keys = list(bibData.keys())
    random.shuffle(keys)        #shuffles the keys aroiund - to run multiple instances of the programm at the same time. Different order, different pdfs get ocred

    for key in keys:            #loops through the bibliography
        bibRecord = bibData[key]

        # 1. create folders, copy files
        functions.processBibRecord(memexPath, bibRecord)

        # 2. OCR the file
        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(memexPath, bibRecord["rCite"], language)


bibData = functions.loadBib(settings["bib_all"])    
processAllRecords(bibData)

# record to regenerate: RossabiReview2011