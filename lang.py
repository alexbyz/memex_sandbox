import functions
import yaml

#creates a file with the language keys and the count

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

bibData = functions.loadBib(settings["bib_all"])

def getLang(bibData):

    tempDic = {}

    for k,v in bibData.items():

        if v["langid"] in tempDic:
            tempDic[v["langid"]] +=1
        
        else:
            tempDic[v["langid"]] = 1
    
    results = []

    for k,v in tempDic.items():
        result = "%010d\t%s" % (v, k)
        results.append(result)

    results = sorted(results, reverse=True)
    results = "\n".join(results)

    with open("lang_analysis.txt", "w", encoding="utf8") as f9:
        f9.write(results)

getLang(bibData)
    
