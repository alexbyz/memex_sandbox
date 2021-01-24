import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs
import yaml 
import os, json

import functions
import huber_interface_functions

###Settings

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">

@ELEMENTCONTENT@

</div>
"""

searchesTemplate = """
<button class="collapsible">SAVED SEARCHES</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>search string</th>
        <th># of publications with matches</th>
        <th>time stamp</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""
#the <th> parts are the table headers -> they get displayed on top  of the table
#each coresponds to a <td> table data (i guess) with the respective contend
publTemplate = """
<button class="collapsible">PUBLICATIONS</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th> 
        <th>author</th>
        <th>date</th>
        <th>title</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

def createIndex(pathToMemex):

    bibData = functions.loadBib(settings["bib_all"])

    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    completeList = []

    for k,v in bibData.items():         
        path = functions.generatePublPath(memexPath, k)     
    	
        entry = "<tr><td><li><a href="+"@PATHTOPUBL@/pages/DETAILS.html>"+"[@CITEKEY@]</a></td><td> @AUTHOR@</td> <td>(@DATE@)</td> - <td><i>@TITLE@</i></td></li></tr>" #here I added the <td> in

        entry = entry.replace("@PATHTOPUBL@", path)
        entry = entry.replace("@CITEKEY@", k)
        if "author" in v: 
            entry = entry.replace("@AUTHOR@", v["author"])
        else:
            entry = entry.replace("@AUTHOR@", "MISSING")
        if "date" in v: 
            entry = entry.replace("@DATE@", v["date"])
        else:
            entry = entry.replace("@DATE@", "MISSING")
        if "title" in v: 
            entry = entry.replace("@TITLE@", v["title"])
        else:
            entry = entry.replace("@TITLE@", "MISSING")
        
        completeList.append(entry)  #print each entry into a list

    content = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(completeList)) #convert the whole contend to a string
    content = content.replace("{","")
    content = content.replace("}","")

    toc = formatSearches(pathToMemex)   #table of contend for all the searches html files is allready prepared by Prof
    template = template.replace("@SEARCHES@", toc)

    #table for publications
    template = template.replace("@PUBLICATIONS@", publTemplate.replace("@TABLECONTENTS@", content)) #publTable is analog to Profs searchesTemplate. I put all the publications in 
    
    with open("index.html", "w", encoding="utf8") as f9:
        f9.write(template)

def processAllEntries(pathToMemex):

    bibData = functions.loadBib(settings["bib_all"])    #loads the bib file
    
    for k,v in bibData.items():      
        
        path = functions.generatePublPath(memexPath, k)
        path = path + "\\" + k +".bib" 
        huber_interface_functions.generatePublicationInterface(k, path)    

# generate search pages and TOC
def formatSearches(pathToMemex):
    with open(settings["template_search"], "r", encoding="utf8") as f1:
        indexTmpl = f1.read()
    dof = functions.dicOfRelevantFiles(pathToMemex, ".searchResults")

    toc = []
    for file, pathToFile in dof.items():
        searchResults = []
        data = json.load(open(pathToFile, encoding="utf8"))
        
        # collect toc
        template = "<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td></tr>"

        linkToSearch = os.path.join("_data\\searches", file+".html")
        pathToPage = '<a href="%s"><i>read</i></a>' % linkToSearch
        searchString = '<div class="searchString">%s</div>' % data.pop("searchString")
        timeStamp = data.pop("timestamp")
        tocItem = template % (pathToPage, searchString, len(data), timeStamp)
        toc.append(tocItem)

        # generate the results page
        keys = sorted(data.keys(), reverse=True)
        for k in keys:
            searchResSingle = []
            results = data[k]
            temp = k.split("::::")
            header = "%s (pages with results: %d)" % (temp[1], int(temp[0]))
            for page, excerpt in results.items():
                pdfPage = int(page)
                linkToPage = '<a href="../%s"><i>go to the original page...</i></a>' % excerpt["pathToPage"]
                searchResSingle.append("<li><b><hr>(pdfPage: %d)</b><hr> %s <hr> %s </li>" % (pdfPage, excerpt["result"], linkToPage))
            searchResSingle = "<ul>\n%s\n</ul>" % "\n".join(searchResSingle)
            searchResSingle = generalTemplate.replace("@ELEMENTHEADER@", header).replace("@ELEMENTCONTENT@", searchResSingle)
            searchResults.append(searchResSingle)
        
        searchResults = "<h2>SEARCH RESULTS FOR: <i>%s</i></h2>\n\n" % searchString + "\n\n".join(searchResults)
        with open(pathToFile.replace(".searchResults", ".html"), "w", encoding="utf8") as f9:
            f9.write(indexTmpl.replace("@MAINCONTENT@", searchResults))

    toc = searchesTemplate.replace("@TABLECONTENTS@", "\n".join(toc))
    return(toc)

#processAllEntries(memexPath)
createIndex(memexPath)

