import os, shutil, re
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"     #load settings
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile):

    bibDic = {}         #empty dict
    recordsNeedFixing = []  #empty list

    with open(bibTexFile, "r", encoding="utf8") as f1:  #open bibfile
        records = f1.read().split("\n@")        #split into the differen records

        for record in records[1:]:              #loop through all of them
            # let process ONLY those records that have PDFs
            
            if ".pdf" in record.lower():
                completeRecord = "\n@" + record #adds an newline and @ at the beginning

                record = record.strip().split("\n")[:-1]    #spilts at new line, get rid of the last empty element

                rType = record[0].split("{")[0].strip()     #first element record type
                rCite = record[0].split("{")[1].strip().replace(",", "")    #second citekey

                bibDic[rCite] = {}      #empty dict at the key citekey
                bibDic[rCite]["rCite"] = rCite  #at the key "citekey" add the citekey of the processed record
                bibDic[rCite]["rType"] = rType  #at the key "recordtype" the recordtype as value
                bibDic[rCite]["complete"] = completeRecord #at the citekey complete add the complete record

                for r in record[1:]:
                    key = r.split("=")[0].strip()
                    val = r.split("=")[1].strip()
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # fix the path to PDF
                    if key == "file":   #gets the path from the record
                        if ";" in val:  #splits it at the ;
                            #print(val)
                            temp = val.split(";")   #gets the parts

                            for t in temp:          #looks for the first pdf
                                if ".pdf" in t:
                                    val = t

                            bibDic[rCite][key] = val    #adds it to the directory

    print("="*80)       #print the number of the processed records
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# generate path from bibtex code, and create a folder, if does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()   #all lowercase
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)    #joins it all together to a path
    return(directory)

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])   #creates path

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath):    #check if path exists
        os.makedirs(tempPath)           #make directory

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"])    #creates path for the individual bib file
        with open(bibFilePath, "w", encoding="utf8") as f9:                     #creates bib file 
            f9.write(bibRecDict["complete"])    #writes in the new file the complete record

        pdfFileSRC = bibRecDict["file"]         #source path

        #betterbibtex escaped : amd \, this replaces \: with : 
        pdfFileSRC = pdfFileSRC.replace("\\:", ":")

        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) #path for the destination, renaming the pdf
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST) #copies file


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData):
    for k,v in bibData.items():     #loops through all the records
        processBibRecord(memexPath, v)
        #print(k, v)

#the "actuall" programm
bibData = loadBib(settings["bib_all"])     #loads in the bibfile 
processAllRecords(bibData)                 #processes all 

print("Done!")