import os, json

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# FUNCTIONS ###############################################
###########################################################

# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile):
    print("="*80)
    print(citeKey)

    jsonFile = pathToBibFile.replace(".bib", ".json")
    with open(jsonFile) as jsonData:
        ocred = json.load(jsonData)
        pNums = ocred.keys()

        pageDic = functions.generatePageLinks(pNums)

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # load individual bib record
        bibFile = pathToBibFile
        bibDic = functions.loadBib(bibFile) #use the load bib to load the ind, bibliographies
        bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])

        orderedPages = list(pageDic.keys()) #convert to list

        for o in range(0, len(orderedPages)):   #loop through all the pages
            #print(o)
            k = orderedPages[o]         #k = current page
            v = pageDic[orderedPages[o]] #v = value of the current page

            pageTemp = template
            pageTemp = pageTemp.replace("@PAGELINKS@", v)   #place the current page into the template page
            pageTemp = pageTemp.replace("@PATHTOFILE@", "") 
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)   #add citekey too

            if k != "DETAILS":  #not the details page = bib file Contend
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k)  #format template, add the scan
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)   #add the scanded page to the html file
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>"))   #add the ocred text 
            else:
                mainElement = bibForHTML.replace("\n", "<br> ")     
                mainElement = '<div class="bib">%s</div>' % mainElement #add the detail in
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">'   #add the formate for the wordcloud
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)                   #add it into the html
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "")                           #here is no ocred text

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            if k == "DETAILS":              #create the links   after details comes the first page, before no page
                nextPage = "0001.html"
                prevPage = ""
            elif k == "0001":               #before the fist page comes detailes
                nextPage = "0002.html"
                prevPage = "DETAILS.html"
            elif o == len(orderedPages)-1:  #last page? then there is no next
                nextPage = ""
                prevPage = orderedPages[o-1] + ".html"
            else:                           #other pages in between
                nextPage = orderedPages[o+1] + ".html"
                prevPage = orderedPages[o-1] + ".html"

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) #add the links into the html
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage)

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k)  #create a path to save the new html file into
            with open(pagePath, "w", encoding="utf8") as f9:    #save the html(string) into a proper html file
                f9.write(pageTemp)

# generate the INDEX and the CONTENTS pages
def generateMemexStartingPages(pathToMemex):
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:  #loads in the template page
        template = ft.read()

    # add index.html
    with open(settings["content_index"], "r", encoding="utf8") as fi:
        indexData = fi.read()
        with open(os.path.join(pathToMemex, "index.html"), "w", encoding="utf8") as f9:
            f9.write(template.replace("@MAINCONTENT@", indexData))

    # load bibliographical data for processing
    publicationDic = {} # key = citationKey; value = recordDic

    for subdir, dirs, files in os.walk(pathToMemex):    
        for file in files:
            if file.endswith(".bib"):       
                pathWhereBibIs = os.path.join(subdir, file)
                tempDic = functions.loadBib(pathWhereBibIs)
                publicationDic.update(tempDic)

    # generate data for the main CONTENTS
    singleItemTemplate = '<li><a href="@RELATIVEPATH@/pages/DETAILS.html">[@CITATIONKEY@]</a> @AUTHOROREDITOR@ (@DATE@) - <i>@TITLE@</i></li>'
    contentsList = []

    for citeKey,bibRecord in publicationDic.items():
        relativePath = functions.generatePublPath(pathToMemex, citeKey).replace(pathToMemex, "")

        authorOrEditor = "[No data]"
        if "editor" in bibRecord:
            authorOrEditor = bibRecord["editor"]
        if "author" in bibRecord:
            authorOrEditor = bibRecord["author"]

        date = bibRecord["date"][:4]

        title = bibRecord["title"]

        # forming a record
        recordToAdd = singleItemTemplate
        recordToAdd = recordToAdd.replace("@RELATIVEPATH@", relativePath)
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", citeKey)
        recordToAdd = recordToAdd.replace("@AUTHOROREDITOR@", authorOrEditor)
        recordToAdd = recordToAdd.replace("@DATE@", date)
        recordToAdd = recordToAdd.replace("@TITLE@", title)

        recordToAdd = recordToAdd.replace("{", "").replace("}", "")

        contentsList.append(recordToAdd)

    contents = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(contentsList))
    mainContent = "<h1>CONTENTS of MEMEX</h1>\n\n" + contents

    # save the CONTENTS page
    with open(os.path.join(pathToMemex, "contents.html"), "w", encoding="utf8") as f9:
        f9.write(template.replace("@MAINCONTENT@", mainContent))

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#generatePublicationInterface("AshkenaziHoly2014", "./_memex_sandbox/_data/a/as/AshkenaziHoly2014/AshkenaziHoly2014.bib")

###########################################################
# PROCESS ALL RECORDS: ANOTHER APPROACH ###################
###########################################################

# Until now we have been processing our publications through
# out bibTeX file; we can also consider a slightly different
# approach that will be more flexible.

def processAllRecords(pathToMemex):
    files = functions.dicOfRelevantFiles(pathToMemex, ".bib")
    for citeKey, pathToBibFile in files.items():
        #print(citeKey)
        generatePublicationInterface(citeKey, pathToBibFile)
    generateMemexStartingPages(pathToMemex)

processAllRecords(settings["path_to_memex"])

# HOMEWORK:
# - give all functions: task - to write a function that process everything
# - give a half-written TOC function which creates an index file;
#   they will need to finish it by adding generation of the TOC file