from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json, yaml
import functions

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

def createWordCloud(savePath, tfIdfDic):
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                   relative_scaling=0.5, colormap="gray") 
    wc.generate_from_frequencies(tfIdfDic)
    # plotting
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    #plt.show() # this line will show the plot
    plt.savefig(savePath, dpi=200, bbox_inches='tight')

def createAll(filename):
    docData = json.load(open(filename, "r", encoding="utf8"))

    for k, v in docData.items():
        savePath = functions.generatePublPath(memexPath, k)
        savePath = savePath + "\\wordcloud"
        if v:
            createWordCloud(savePath, v)

createAll("tfidfTableDic_filtered.txt")