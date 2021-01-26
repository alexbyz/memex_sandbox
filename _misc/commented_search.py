import re, os, yaml, json, random
from datetime import datetime

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# FUNCTIONS ###############################################
###########################################################

#dict structure:
# {
#       "Matches::::Citekey": {
#           "pagenumber": {
#               "matches": number,
#               "pathToPage": "path to html",
#               "result": "text"
#           }
#           "nextpage":{ ...
#           }
#           ...          
#       },
#       "Matches::::nextPublication": {...
#       },
#       "searchString": "Search",
#       "timestamp": "Time"
# }


def searchOCRresults(pathToMemex, searchString):
    print("SEARCHING FOR: `%s`" % searchString)
    files = functions.dicOfRelevantFiles(pathToMemex, ".json")  #returns us a dirct with all the json file, citeKey as KEy and the paths as values
    results = {}

    for citationKey, pathToJSON in files.items():          #loop through all of them    
        data = json.load(open(pathToJSON))                 #load the current json file ->OCRed Text
        #print(citationKey)
        count = 0                                           #count

        for pageNumber, pageText in data.items():           #page Number as key, Text as value
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE):  #search each page for the searchString
                if citationKey not in results:
                    results[citationKey] = {}               #if in the results dict is no entry allready create and empyty sub dict with the citekey as key

                # relative path
                a = citationKey.lower()                     #save citekey
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber)  #create path for the html page with the page number with a match
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE))   #count all matches in the page
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText, flags=re.IGNORECASE) #highlight the searchstring in the results

                results[citationKey][pageNumber] = {}   #create empty dict with the page number as key - all other data will fo into this
                results[citationKey][pageNumber]["pathToPage"] = relPath    #add the path
                results[citationKey][pageNumber]["matches"] = countM        #add the count
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>")   #add the text

                count  += 1 #count pages with results up

        if count > 0:   #if there are results
            print("\t", citationKey, " : ", count)  #print how many at this page
            newKey = "%09d::::%s" % (count, citationKey)    
            results[newKey] = results.pop(citationKey)  #add the number of matches to the citekey

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  #current time
            results["timestamp"] = currentTime      #added as a timestamp
            # add search string (as submitted)
            results["searchString"] = searchString  #add search string

    saveWith = re.sub("\W+", "", searchString)  
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith)
    with open(saveTo, 'w', encoding='utf8') as f9c: #save the search with a recognizeable name
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False)

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

searchPhrase  = r"corpus\W*based"
#searchPhrase  = r"corpus\W*driven"
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], searchPhrase)
#exec(open("9_Interface_IndexPage.py").read())