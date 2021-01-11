import yaml 
import os, json
import re
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

import functions


###Settings

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
language = settings["language_keys"]
min_Df_S = settings["min_df"]
max_Df_S = settings["max_df"]

def generatetfidfvalues():
    ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
    citeKeys = list(ocrFiles.keys())

    docList   = []
    docIdList = []

    stopwFile = "./_misc/stopwords.yml"
    stopW = yaml.load(open(stopwFile, encoding="utf8"))

    stopW_list = []
    for k, v in stopW.items():
        stopW_list.append(v)

    for citeKey in citeKeys:
        docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8"))
               
        docId = citeKey
        doc   = " ".join(docData.values())

        doc   = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc   = re.sub('\W+', ' ', doc)
        doc   = re.sub('\d+', ' ', doc)
        doc   = re.sub(' +', ' ', doc)

        docList.append(doc)
        docIdList.append(docId)


    #convert data
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=min_Df_S, max_df=max_Df_S, stop_words=stopW)
    countVectorized = vectorizer.fit_transform(docList)
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    vectorized = tfidfTransformer.fit_transform(countVectorized) # https://en.wikipedia.org/wiki/Sparse_matrix
    cosineMatrix = cosine_similarity(vectorized)

    #converting results
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
    print("tfidfTable Shape: ", tfidfTable.shape) # optional
    tfidfTable = tfidfTable.transpose()
    tfidfTableDic = tfidfTable.to_dict()

    cosineTable = pd.DataFrame(cosineMatrix)
    print("cosineTable Shape: ", cosineTable.shape) # optional
    cosineTable.columns = docIdList
    cosineTable.index = docIdList
    cosineTableDic = cosineTable.to_dict()

    filteredDic = {}
    filteredDic = functions.filterDic(tfidfTableDic, 0.05)
    with open("tfidfTableDic_filtered.txt", 'w', encoding='utf8') as f9:
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)

    filteredDic = {}
    filteredDic = functions.filterDic(cosineTableDic, 0.25)

    with open("cosineTableDic_filtered.txt", 'w', encoding='utf8') as f9:
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)

generatetfidfvalues()