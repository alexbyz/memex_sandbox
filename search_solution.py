import re, os, yaml, json, random
from datetime import datetime

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString):
    print("SEARCHING FOR: `%s`" % searchString)
    files = functions.dicOfRelevantFiles(pathToMemex, ".json")
    results = {}

    for citationKey, pathToJSON in files.items():
        data = json.load(open(pathToJSON, encoding="utf8"))
        #print(citationKey)
        count = 0

        for pageNumber, pageText in data.items():
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE):
                if citationKey not in results:
                    results[citationKey] = {}

                # relative path
                a = citationKey.lower()
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber)
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE))
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'><i style='color:red'>\1</i></span>", pageText, flags=re.IGNORECASE)

                results[citationKey][pageNumber] = {}
                results[citationKey][pageNumber]["pathToPage"] = relPath
                results[citationKey][pageNumber]["matches"] = countM
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>")

                count  += 1

        if count > 0:
            print("\t", citationKey, " : ", count)
            newKey = "%09d::::%s" % (count, citationKey)
            results[newKey] = results.pop(citationKey)

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            results["timestamp"] = currentTime
            # add search string (as submitted)
            results["searchString"] = searchString

    saveWith = re.sub("\W+", "", searchString)
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith)
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False)


###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

#searchPhrase  = r"\b(b|B)alkan\b"
#searchPhrase  = r"\b(T|t)hessaloniki\b"
#searchPhrase  = r"\bDemetrius\b"
#searchPhrase  = r"\b(n|N)ika\b"
#searchPhrase  = r"(Kaiser|emperor)"
#searchPhrase  = r"acclamation"


searchOCRresults(settings["path_to_memex"], searchPhrase)

