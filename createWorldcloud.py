#from wordcloud import WordCloud
#import matplotlib.pyplot as plt

# def createWordCloud(savePath, tfIdfDic):
#     wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
#                    relative_scaling=0.5, colormap="gray") 
#     wc.generate_from_frequencies(tfIdfDic)
#     # plotting
#     plt.imshow(wc, interpolation="bilinear")
#     plt.axis("off")
#     #plt.show() # this line will show the plot
#     plt.savefig(savePath, dpi=200, bbox_inches='tight')

def loadTfIdfFile(filename):
    with open(filename, "r", encoding="utf8") as f1:
        loaded = f1.read()
        print(type(loaded))

loadTfIdfFile("tfidfTableDic_filtered.txt")