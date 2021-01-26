###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

from wordcloud import WordCloud
import matplotlib.pyplot as plt

AndrewsTree2013 = {         #example from the tfidf file
        "academic": 0.05813626462255791, "acyclic": 0.06250123247317078,
        "andrews": 0.12638860902474044,
        "artificial": 0.07179606130684399,
        "coincidental": 0.107968929904822,
        "collatex": 0.05992322690922588,
        "collation": 0.06303029408091644,
        "computational": 0.05722784996783764,
        "computing": 0.10647437138201694,
        "conflation": 0.06207493202469115,
        "copied": 0.11909333470623461,
        "deletion": 0.1139260485820703,
        "deum": 0.08733065096290674,
        "dsh": 0.12062758085160386,
        "empirical": 0.06256016440693514,
        "exemplar": 0.06413026390502427,
        "february": 0.06598308140156786,
        "fig": 0.06658631708313895,
        "figure": 0.057484475246214396,
        "finnish": 0.06718916017623287,
        "genealogical": 0.14922848147612744,
        "grammatical": 0.06639003369358097,
        "graph": 0.3064885690820798,
        "heikkila": 0.06250123247317078,
        "howe": 0.0502983742283863,
        "lachmannian": 0.05357248497700353,
        "legend": 0.05576734763473662,
        "lexical": 0.07504108167413616,
        "library": 0.052654345617120235,
        "linguistic": 0.08295373338961148,
        "literary": 0.05453901405048022,
        "macé": 0.09416507085735495,
        "manuscript": 0.056407679242811995,
        "medieval": 0.0722276960100237,
        "methods": 0.06617794961055612,
        "model": 0.06712481163842804,
        "oup": 0.11328056728336285,
        "phylogenetic": 0.0771729868291211,
        "quae": 0.06207493202469115,
        "readings": 0.14004936139939653,
        "relationships": 0.05294605101492676,
        "reverted": 0.08384604576952619,
        "roos": 0.057864729221843304,
        "root": 0.050044699046501814,
        "sermo": 0.05136276592219361,
        "spelling": 0.10943421974916011,
        "spencer": 0.058047262455825824,
        "stemma": 0.42250289612460745,
        "stemmata": 0.0813887983497219,
        "stemmatic": 0.09093028877718234,
        "stemmatology": 0.11984645381845176,
        "table": 0.0650730361130049,
        "traditions": 0.06135920913100084,
        "transmission": 0.07196157976331963,
        "transposition": 0.09182278547380966,
        "tree": 0.06790095059625004,
        "user": 0.08246083727188196,
        "variant": 0.2562367460915465,
        "variants": 0.1432698250058143,
        "variation": 0.2935924450487041,
        "vb": 0.11035543471056206,
        "vertices": 0.050436368099886865,
        "vienna": 0.07506704856975273,
        "witness": 0.11471933221048437,
        "witnesses": 0.09101116903971758
    }

savePath = "AndrewsTree2013"

def createWordCloud(savePath, tfIdfDic):    
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2, relative_scaling=0.5, colormap="gray") #settings for the wordcloud

    wc.generate_from_frequencies(tfIdfDic)     #generate the wordcloud from the tfidf
    # plotting
    plt.imshow(wc, interpolation="bilinear")   #plot the wordcloud
    plt.axis("off")
    #plt.show() # this line will show the plot
    plt.savefig(savePath, dpi=200, bbox_inches='tight') #save it

createWordCloud(savePath, AndrewsTree2013)

# NEW LIBRARIES
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

import os, json, re, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generateWordCloud(citeKey, pathToFile):
    # aggregate dictionary
    data = json.load(open(pathToFile))  #loads the tfidf file
    dataNew = {}                        #empty dict
    for page,pageDic in data.items():   #loop through loaded data
        for term, tfIdf in pageDic.items(): 
            if term in dataNew:         
                dataNew[term] += tfIdf
            else:
                dataNew[term]  = tfIdf

def filterTfidfDictionary(dictionary, threshold, lessOrMore):   #filters the dict at a given threshold, either above or below
    dictionaryFilt = {}
    for item1, citeKeyDist in dictionary.items():
        dictionaryFilt[item1] = {}
        for item2, value in citeKeyDist.items():
            if lessOrMore == "less":
                if value <= threshold:
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            elif lessOrMore == "more":
                if value >= threshold:
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`")

        if dictionaryFilt[item1] == {}:
            dictionaryFilt.pop(item1)
    return(dictionaryFilt)


def generateTfIdfWordClouds(pathToMemex):
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json")   #all json files ->OCR Results
    citeKeys = list(ocrFiles.keys())#[:500]

    print("\taggregating texts into documents...")
    docList   = []
    docIdList = []

    for citeKey in citeKeys:    #loads all the json files
        docData = json.load(open(ocrFiles[citeKey]))
        
        docId = citeKey
        doc   = " ".join(docData.values())

        # clean doc
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc = re.sub('\W+', ' ', doc)
        doc = re.sub('_+', ' ', doc)
        doc = re.sub('\d+', ' ', doc)
        doc = re.sub(' +', ' ', doc)

        # update lists
        docList.append(doc)
        docIdList.append(docId)

    print("\t%d documents generated..." % len(docList))

    # PART 2: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...")

    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=2, max_df=0.5)
    countVectorized = vectorizer.fit_transform(docList)
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    vectorized = tfidfTransformer.fit_transform(countVectorized) # generates a sparse matrix

    print("\tconverting and filtering tfidf data...")
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
    tfidfTable = tfidfTable.transpose()
    tfidfTableDic = tfidfTable.to_dict()
    tfidfTableDic = filterTfidfDictionary(tfidfTableDic, 0.02, "more")
    

    #tfidfTableDic = json.load(open("/Users/romanovienna/Dropbox/6.Teaching_New/BUILDING_MEMEX_COURSE/_memex_sandbox/_data/results_tfidf_publications.dataJson"))

    # PART 4: generating wordclouds
    print("\tgenerating wordclouds...")
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                relative_scaling=0.5, #color_func=lambda *args, **kwargs: (179,0,0)) # single color
                #colormap="copper") # Oranges, Reds, YlOrBr, YlOrRd, OrRd; # copper
                colormap="gray") # binary, gray
                # https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html

    counter = len(tfidfTableDic)
    citeKeys = list(tfidfTableDic.keys())
    random.shuffle(citeKeys)

    for citeKey in citeKeys:    #creates them unordered --> to allow script to run parallel
        savePath = functions.generatePublPath(pathToMemex, citeKey)
        savePath = os.path.join(savePath, "%s_wCloud.jpg" % citeKey)

        if not os.path.isfile(savePath):
            wc.generate_from_frequencies(tfidfTableDic[citeKey])
            # plotting
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            #plt.show() # this line shows the plot
            plt.savefig(savePath, dpi=200, bbox_inches='tight')

            print("\t%s (%d left...)" % (citeKey, counter))
            counter -= 1
        
        else:
            print("\t%s --- already done" % (citeKey))
            counter -= 1

        # WordCloud:
        #   colormap: https://matplotlib.org/3.3.3/tutorials/colors/colormaps.html
        #   font_path="./fonts/Baskerville.ttc" (path to where your font is)
        #   Documentation: https://amueller.github.io/word_cloud/index.html
        #input("Check the plot!")

###########################################################
# PROCESS ALL RECORDS: WITH PROMPT ########################
###########################################################

print("""
============= GENERATING WORDCLOUDS ===============     
   Type "YES", if you want to regenerate new files;
Old files will be deleted and new ones regenerated;
Press `Enter` to continue generating missing files.
===================================================
""")
response = input()

if response.lower() == "yes":
    print("Deleting existing files...")
    functions.removeFilesOfType(settings["path_to_memex"], "_wCloud.jpg")
    print("Generating new files...")
    generateTfIdfWordClouds(settings["path_to_memex"])
else:
    print("Getting back to generating missing files...")
    generateTfIdfWordClouds(settings["path_to_memex"])