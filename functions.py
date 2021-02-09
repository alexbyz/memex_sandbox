#functions

import os, json
import pdf2image, pytesseract
import PyPDF2  
import yaml, re
from datetime import datetime

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
popplerPath = settings["path_to_poppler"]

# generate path from bibtex code:
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)

    return(directory)

#############################
# REUSING FUNCTIONS #########
#############################

def removeCommentsFromPDF(pathToPdf):
    try:
        with open(pathToPdf, 'rb') as pdf_obj:
            pdf = PyPDF2.PdfFileReader(pdf_obj)
            out = PyPDF2.PdfFileWriter()
            for page in pdf.pages:
                out.addPage(page)
                out.removeLinks()
            tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf")
            with open(tempPDF, 'wb') as f: 
                out.write(f)
        return(tempPDF)
    except: 
        return False

def ocrPublication(pathToMemex, citationKey, language):
    publPath = generatePublPath(pathToMemex, citationKey)    
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json")
    saveToPath = os.path.join(publPath, "pages")

    pdfFileTemp = removeCommentsFromPDF(pdfFile)


    if pdfFileTemp != False:

        if not os.path.isfile(jsonFile):
            if not os.path.exists(saveToPath):
                os.makedirs(saveToPath)
        
                print("\t>>> OCR-ing: %s" % citationKey)

                textResults = {}
                images = pdf2image.convert_from_path(pdfFileTemp, poppler_path= popplerPath)
                pageTotal = len(images)
                pageCount = 1
                for image in images:
                    image = image.convert('1')
                    finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
                    image.save(finalPath, optimize=True, quality=10)

                    text = pytesseract.image_to_string(image, lang=language)
                    textResults["%04d" % pageCount] = text

                    print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
                    pageCount += 1

                with open(jsonFile, 'w', encoding='utf8') as f9:
                    json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
            else:            
                print("\t>>> %s has already been OCR-ed..." % citationKey)            

        os.remove(pdfFileTemp)
    else:
        print("="*80)
        print("Something wrong with the file")
        print("="*80)

# load bibTex Data into a dictionary
def loadBib(bibTexFile):

    bibDic = {}
    recordsNeedFixing = []

    with open(bibTexFile, "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower():
                completeRecord = "\n@" + record

                record = record.strip().split("\n")[:-1]

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord

                for r in record[1:]:
                    key = r.split("=")[0].strip()
                    val = r.split("=")[1].strip()
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # fix the path to PDF
                    if key == "file":
                        if ";" in val:
                            #print(val)
                            temp = val.split(";")

                            for t in temp:
                                if ".pdf" in t:
                                    val = t

                            bibDic[rCite][key] = val

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# generate path from bibtex code, and create a folder, if does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`

# creates a dictionary of citationKey:Path pairs for a relevant type of files
def dicOfRelevantFiles(pathToMemex, extension):
    dic = {}
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication tf data
            if file.endswith(extension):
                key = file.replace(extension, "")
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)

def filterDic(dic, thold): 

    retDic = {}    #empty Dictonary to copy filterd values into

    for k,v in dic.items():     #loop through outer first dic, containig the titles
        retDic[k]={}            #create a subDic for each title

        for key,val in v.items():   #loop through the entries of each title
            if val > thold:         #check threshold                            
                if k != key:        #check to not match the publication with itself
                    retDic[k][key] = val    #add value

    return(retDic)

def createWordCloud(savePath, tfIdfDic):
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                   relative_scaling=0.5, colormap="gray") 
    wc.generate_from_frequencies(tfIdfDic)
    # plotting
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    #plt.show() # this line will show the plot
    plt.savefig(savePath, dpi=200, bbox_inches='tight')

def loadMultiLingualStopWords(listOfLanguageCodes):
    print(">> Loading stopwords...")
    stopwords = []
    pathToFiles = settings["stopwords"]
    codes = json.load(open(os.path.join(pathToFiles, "languages.json"), encoding="utf8"))

    for l in listOfLanguageCodes:
        with open(os.path.join(pathToFiles, codes[l]+".txt"), "r", encoding="utf8") as f1:
            lang = f1.read().strip().split("\n")
            stopwords.extend(lang)

    stopwords = list(set(stopwords))
    print("\tStopwords for: ", listOfLanguageCodes)
    print("\tNumber of stopwords: %d" % len(stopwords))
    #print(stopwords)
    return(stopwords)

# creates a list of paths to files of a relevant type
def listOfRelevantFiles(pathToMemex, extension):
    listOfPaths = []
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication tf data
            if file.endswith(extension):
                path = os.path.join(subdir, file)
                listOfPaths.append(listOfPaths)
    return(listOfPaths)

def memexStatusUpdates(pathToMemex, fileType):
    # collect stats
    NumberOfPublications = len(listOfRelevantFiles(pathToMemex, ".pdf")) # PDF is the main measuring stick
    NumberOfCountedItems = len(listOfRelevantFiles(pathToMemex, fileType))

    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # check if dictionary exists
    dicFile = os.path.join(pathToMemex, "memex.status")
    if os.path.isfile(dicFile):
        dic = json.load(open(dicFile, encoding="utf8"))
    else:
        dic = {}

    dic[fileType] = {}
    dic[fileType]["files"] = NumberOfCountedItems
    dic[fileType]["pdfs"] = NumberOfPublications
    dic[fileType]["time"] = currentTime

    # save dic
    with open(dicFile, 'w', encoding='utf8') as f9:
        json.dump(dic, f9, sort_keys=True, indent=4, ensure_ascii=False)

    print("="*40)
    print("Memex Stats have been updated for: %s" % fileType)
    print("="*40)

# the function will quickly remove all files with a certain
# extension --- useful when messing around and need to delete
# lots of temporary files

# HTML: generates TOCs for each page; the current page is highlighted with red
def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)

# HTML: makes BIB more HTML friendly
def prettifyBib(bibText):
    bibText = bibText.replace("{{", "").replace("}}", "")
    bibText = re.sub(r"\n\s+file = [^\n]+", "", bibText)
    bibText = re.sub(r"\n\s+abstract = [^\n]+", "", bibText)
    return(bibText)

