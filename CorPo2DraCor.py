# -*- coding : utf8 -*-
import json
import pathlib
import os
from lxml import etree

print("---start---") # debugging

### namespaces
ns_xml = "http://www.w3.org/XML/1998/namespace"
ns_tei = "http://www.tei-c.org/ns/1.0"

NSMAP = {"xml" : ns_xml,
        "tei" : ns_tei}

dir_source = "data/json/" # source folder
print("taking data from: " + dir_source)

dir_output = "data/xml/" # target folder
print("putting data here: " + dir_output)

### logfile
logfile_path = "data/xml/log.txt" # log file folder & name

print(os.getcwd())

def corpo2dracor(source_path, log_path):
    ### load JSON file
    f = open(source_path, encoding="utf8")
    #print(f) # debugging
    d = json.load(f)
    #print(d) # debugging
    pod_title_main = "Coronavirus-Update Folge " + d["metadata"]["id"] # podcast main title, e.g. "Coronavirus-Update Folge 50"
    pod_title_sub = d["metadata"]["title"] # podcast sub title, e.g. "Das Virus kommt wieder"

    # logfile open in append mode
    f_log = open(log_path, "a")

    ### processing instruction
    prinst = etree.ProcessingInstruction("xml-model", "href='https://dracor.org/schema.rng' type='application/xml' schematypens='http://relaxng.org/ns/structure/1.0'")

    # add root
    root = etree.Element("{%s}TEI" % ns_tei, nsmap = NSMAP)

    ### insert into tree
    tree = etree.ElementTree(root)

    ### second tree for lxml [quickfix, might/should "refactor" the whole script...]
    #tree_lxml = ET2.Element("TEI")

    #tree.getroot().insert(0, prinst)
    tree.getroot().addprevious(prinst)

    #tree.getroot().append(prinst)

    ### basic elements & default values
    #tei_teiHeader = etree.SubElement(root, "{%s}teiHeader" % (ns_tei)) # TEI/teiHeader # delete later
    tei_teiHeader = etree.SubElement(root, "{%s}teiHeader" % ns_tei) # TEI/teiHeader
    tei_fileDesc = etree.SubElement(tei_teiHeader, "{%s}fileDesc" % ns_tei) # TEI/teiHeader/fileDesc
    tei_titleStmt = etree.SubElement(tei_fileDesc, "{%s}titleStmt" % ns_tei) # TEI/teiHeader/fileDesc/titleStmt

    tei_title_main = etree.SubElement(tei_titleStmt, "{%s}title" % ns_tei) # TEI/teiHeader/fileDesc/titleStmt/title[@type=main]
    tei_title_sub = etree.SubElement(tei_titleStmt, "{%s}title" % ns_tei) # TEI/teiHeader/fileDesc/titleStmt/title[@type=sub]

    tei_profileDesc = etree.SubElement(tei_teiHeader, "{%s}profileDesc" % ns_tei) # TEI/teiHeader/profileDesc
    tei_particDesc = etree.SubElement(tei_profileDesc, "{%s}particDesc" % ns_tei) # TEI/teiHeader/profileDesc/particDesc
    tei_listPerson = etree.SubElement(tei_particDesc, "{%s}listPerson" % ns_tei) # TEI/teiHeader/profileDesc/listPerson
    tei_text = etree.SubElement(root, "{%s}text" % ns_tei) # TEI/text

    tei_front = etree.SubElement(tei_text, "{%s}front" % ns_tei) # TEI/text/front

    tei_body = etree.SubElement(tei_text, "{%s}body" % ns_tei) # TEI/text/body
    tei_div = etree.SubElement(tei_body, "{%s}div" % ns_tei) # TEI/text/body/div
    tei_div.set("type", "scene") # TEI/text/body/div@type

    tei_title_main.set("type", "main") # TEI/teiHeader/fileDesc/titleStmt/title[@type="main"]
    tei_title_main.text = pod_title_main # TEI/teiHeader/fileDesc/titleStmt/title[@type="main"].text

    tei_title_sub.set("type", "sub") # TEI/teiHeader/fileDesc/titleStmt/title[@type="sub"]
    tei_title_sub.text = pod_title_sub  # TEI/teiHeader/fileDesc/titleStmt/title[@type="sub"].text

    # author
    for p in d["metadata"]["speakers"]:
        tei_author = etree.SubElement(tei_titleStmt, "{%s}author" % ns_tei) # TEI/teiHeader/fileDesc/titleStmt/author
        
        # convert "firstname lastname" to "lastname, firstname"
        p_first = p.rpartition(" ")[0] # get first name
        p_last = p.partition(" ")[2] # get last name
        p_lastfirst = p_last + ", " + p_first # "lastname, firstname"
        tei_author.text = p_lastfirst # TEI/teiHeader/fileDesc/titleStmt/author.text

        """ 
        # match name with wikidata URI (outsource this later / use list/dict?)
        if p == "Christian Drosten":
            tei_author.set("key", "wikidata:Q1079331") # TEI/teiHeader/fileDesc/titleStmt/author@key
        if p == "Korinna Hennig":
            tei_author.set("key", "wikidata:Q95993043") # TEI/teiHeader/fileDesc/titleStmt/author@key
        """

    tei_publicationStmt = etree.SubElement(tei_fileDesc, "{%s}publicationStmt" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/publisher[xml:id="dracor"]
    tei_publisher = etree.SubElement(tei_publicationStmt, "{%s}publisher" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/publisher
    #tei_publisher.set("xml:id", "dracor") # TEI/teiHeader/fileDesc/publicationStmt/publisher[xml:id="dracor"]
    tei_publisher.set("{%s}id" % ns_xml, "dracor") # TEI/teiHeader/fileDesc/publicationStmt/publisher[xml:id="dracor"]
    tei_publisher.text = "DraCor" # TEI/teiHeader/fileDesc/publicationStmt/publisher.text

    tei_idno_url = etree.SubElement(tei_publicationStmt, "{%s}idno" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/idno[type="URL"]
    tei_idno_url.set("type", "URL") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="URL"]@type
    tei_idno_url.text = "https://dracor.org" # TEI/teiHeader/fileDesc/publicationStmt/idno[type="URL"].text

    tei_idno_dracor = etree.SubElement(tei_publicationStmt, "{%s}idno" % ns_tei)  # TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"]
    tei_idno_dracor.set("type", "dracor") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"]@type
    #tei_idno_dracor.set("xml:base", "https://dracor.org/id/") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"]@xml:base
    tei_idno_dracor.set("{%s}base" % ns_xml, "https://dracor.org/id/") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"]@xml:base

    # construct idno => TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"].text
    pod_id = d["metadata"]["id"]
    if(pod_id != 'missing'): # ID could be missing ("SONDERFOLGE" etc.)
        if(int(pod_id)>0):
            pod_id = int(pod_id)
            if int(pod_id) < 10: # 1 char
                pod_id_idno = "drost" + "00000" + str(pod_id)
            else: 
                if int(pod_id) < 100: # 2 char
                    pod_id_idno = "drost" + "0000" + str(pod_id)
                else:
                    if int(pod_id) < 1000: # 3 char
                        pod_id_idno = "drost" + "000" + str(pod_id)
                    else:
                        if int(pod_id) < 10000: # 4 char
                            pod_id_idno = "drost" + "00" + str(pod_id)
                        else:
                            if int(pod_id) < 100000: # 5 char
                                pod_id_idno = "drost" + "0" + str(pod_id)
                            else:
                                if int(pod_id) < 100000: # 6 char
                                    pod_id_idno = "drost" + "" + str(pod_id)
                                # else:
                                    # Dear future person, I'm really sorry you're still struggling with Covid19. This script was never intended to support more than 100000 episodes.
        else:
            pod_id_idno = "drost" + "" + pod_id
    else:
            pod_id_idno = '' # leave blank
    tei_idno_dracor.text = pod_id_idno # TEI/teiHeader/fileDesc/publicationStmt/idno[type="dracor"].text

    tei_idno_wikidata = etree.SubElement(tei_publicationStmt, "{%s}idno" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/idno[type="wikidata" xml:base="https://www.wikidata.org/entity/"]
    tei_idno_wikidata.set("type", "wikidata") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="wikidata" xml:base="https://www.wikidata.org/entity/"]@type
    #tei_idno_wikidata.set("xml:base", "https://www.wikidata.org/entity/") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="wikidata" xml:base="https://www.wikidata.org/entity/"]@xml:base
    tei_idno_wikidata.set("{%s}base" % ns_xml, "https://www.wikidata.org/entity/") # TEI/teiHeader/fileDesc/publicationStmt/idno[type="wikidata" xml:base="https://www.wikidata.org/entity/"]@xml:base
    tei_idno_wikidata.text = "Q88072607" # TEI/teiHeader/fileDesc/publicationStmt/idno[type="wikidata" xml:base="https://www.wikidata.org/entity/"].text

    tei_availability = etree.SubElement(tei_publicationStmt, "{%s}availability" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/availability
    tei_licence = etree.SubElement(tei_availability, "{%s}licence" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/availability/licence
    etree.SubElement(tei_licence, "{%s}p" % ns_tei).text = "Copyright (C) NDR Info" # TEI/teiHeader/fileDesc/publicationStmt/availability/licence/p
    tei_ref = etree.SubElement(tei_licence, "{%s}ref" % ns_tei) # TEI/teiHeader/fileDesc/publicationStmt/availability/licence/ref
    tei_ref.set("target", "https://www.ndr.de/nachrichten/info/Coronavirus-Update-Die-Podcast-Folgen-als-Skript,podcastcoronavirus102.html") # TEI/teiHeader/fileDesc/publicationStmt/availability/licence/ref@target
    tei_ref.text = "ndr.de" # TEI/teiHeader/fileDesc/publicationStmt/availability/licence/ref.text

    tei_sourceDesc = etree.SubElement(tei_fileDesc, "{%s}sourceDesc" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc
    tei_bibl_digitalSource = etree.SubElement(tei_sourceDesc, "{%s}bibl" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]
    etree.SubElement(tei_bibl_digitalSource, "{%s}name" % ns_tei).text = "ndr.de"  # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/name

    tei_idno = etree.SubElement(tei_bibl_digitalSource, "{%s}idno" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/idno[type="URL"]
    tei_idno.set("type", "URL") # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/idno[type="URL"]@type
    #pod_pdfname_id = (int(d["metadata"]["id"]) * 2) + 100 # construct strange NDR podcast transcript id
    #pod_pdfname =  str(pod_pdfname_id) + ".pdf" # construct pdf name
    #tei_idno.text = "https://www.ndr.de/nachrichten/info/" + pod_pdfname # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/idno[type="URL"].text
    tei_idno.text = d["metadata"]["source"] # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/idno[type="URL"].text
    

    # ATTENTION, pls: do not confuse with # TEI/teiHeader/fileDesc/publicationStmt/availability ! (re-using variable names to avoid variable name complexity...)
    tei_availability = etree.SubElement(tei_bibl_digitalSource, "{%s}availability" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/availability
    tei_licence = etree.SubElement(tei_availability, "{%s}licence" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/availability/licence

    tei_bibl_originalSource = etree.SubElement(tei_bibl_digitalSource, "{%s}bibl" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]
    etree.SubElement(tei_bibl_originalSource, "{%s}title" % ns_tei).text = pod_title_main # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]/title
    tei_date = etree.SubElement(tei_bibl_originalSource, "{%s}date" % ns_tei) # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]/date
    tei_date.set("type","premiere") # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]/date@type
    tei_date.set("when", "") # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]/date@when
    tei_date.text = "" # TEI/teiHeader/fileDesc/sourceDesc/bibl[type="digitalSource"]/bibl[type="originalSource"]/date.text

    tei_textClass = etree.SubElement(tei_profileDesc, "{%s}textClass" % ns_tei) # TEI/teiHeader/profileDesc/textClass
    tei_keywords = etree.SubElement(tei_textClass, "{%s}keywords" % ns_tei) # TEI/teiHeader/profileDesc/textClass/keywords
    tei_term = etree.SubElement(tei_keywords, "{%s}term" % ns_tei) # TEI/teiHeader/profileDesc/textClass/keywords/term
    tei_term.set("type", "genreTitle") # TEI/teiHeader/profileDesc/textClass/keywords/term@type

    tei_docTitle = etree.SubElement(tei_front, "{%s}docTitle" % ns_tei) # TEI/text/front/docTitle
    tei_titlePart_main = etree.SubElement(tei_docTitle, "{%s}titlePart" % ns_tei) # TEI/text/front/docTitle/titlePart[type="main"]
    tei_titlePart_main.set("type", "main") # TEI/text/front/docTitle/titlePart[type="main"]@type
    tei_titlePart_main.text = pod_title_main # TEI/text/front/docTitle/titlePart[type="main"].text
    tei_titlePart_sub = etree.SubElement(tei_docTitle, "{%s}titlePart" % ns_tei) # TEI/text/front/docTitle/titlePart[type="sub"]
    tei_titlePart_sub.set("type", "sub") # TEI/text/front/docTitle/titlePart[type="sub"]@type
    tei_titlePart_sub.text = pod_title_sub # TEI/text/front/docTitle/titlePart[type="sub"].text

    tei_castList = etree.SubElement(tei_front, "{%s}castList" % ns_tei) # TEI/text/front/castList

    # loop through speakers
    for p in d["metadata"]["speakers"]:
        tei_castItem = etree.SubElement(tei_castList, "{%s}castItem" % ns_tei) # TEI/text/front/castList/castItem    
        etree.SubElement(tei_castItem, "{%s}name" % ns_tei).text = p # TEI/text/front/castList/castItem/name.text
        # match name with role (outsource this later / use list?)
        if p == "Christian Drosten":
            etree.SubElement(tei_castItem, "{%s}roleDesc" % ns_tei).text = "Virologe, Charité Berlin" # TEI/text/front/castList/castItem/roleDesc.text
        if p == "Korinna Hennig":
            etree.SubElement(tei_castItem, "{%s}roleDesc" % ns_tei).text = "Wissenschaftsredakteurin, NDR Info" # TEI/text/front/castList/castItem/roleDesc.text

    ### specific elements / fill in content

    # listPerson
    for p in d["metadata"]["speakers"]:
        tei_person =  etree.SubElement(tei_listPerson, "{%s}person" % ns_tei) # TEI/teiHeader/profileDesc/listPerson
        # IDfy person name
        p_id = p.replace(" ", "_")
        p_id = p_id.lower()
        #tei_person.set("xml:id",p_id) # TEI/teiHeader/profileDesc/listPerson/person@xml:id
        tei_person.set("{%s}id" % ns_xml,p_id) # TEI/teiHeader/profileDesc/listPerson/person@xml:id
        etree.SubElement(tei_person,"{%s}persName" % ns_tei).text = p # TEI/teiHeader/profileDesc/listPerson/person.text
        # match name with sex (outsource this later / use list/dict?)
        if p == "Christian Drosten":
            tei_person.set("sex", "MALE") # TEI/teiHeader/profileDesc/listPerson/person@sex
        if p == "Korinna Hennig":
            tei_person.set("sex", "FEMALE") # TEI/teiHeader/profileDesc/listPerson/person@sex


    # ??? # TEI/text/body/div[type="scene"]/head
    # ??? # TEI/text/body/div[type="scene"]/stage

    # p
    for i in range (1,len(d["content"])-1):
        tei_sp = etree.SubElement(tei_div, "{%s}sp" % ns_tei) # TEI/text/body/div/sp

        # get speaker name and "IDfy" it
        p = d["content"][str(i)][0]
        p_id = p.replace(" ", "_")
        p_id = "#" + p_id.lower()
        tei_sp.set("who", p_id) # TEI/text/body/div/sp@who

        etree.SubElement(tei_sp, "{%s}speaker" % ns_tei).text = p # TEI/text/body/div/sp/speaker

        # add text
        tei_p = etree.SubElement(tei_sp, "{%s}p" % ns_tei) # TEI/text/body/div[type="scene"]/sp/p
        tei_p.text = d["content"][str(i)][1] # TEI/text/body/div[type="scene"]/sp/p.text


        #debugging (searching for speaker == none...)
        if (p_id == "#none"):
            #print("Datei: " + pathlib.Path(source_path).stem)
            #print("p: " + str(i))
            #print(p_id)
            #print(tei_p.text)
            logstr = "TranskriptNr & p: " + pathlib.Path(source_path).stem + "." + str(i) + "." + p_id + ": " + tei_p.text
            f_log.write(logstr)
            f_log.write("\n")
            f_log.write("\n")

    # prettify / indent
    etree.indent(root, space="\t", level=0)

    ### write file

    # get file name without extension
    file_name_woext = pathlib.Path(source_path).stem

    #print(file_name_woext) # debugging

    # write
    tree.write(dir_output + file_name_woext + ".xml", encoding = "UTF-8", pretty_print = True , xml_declaration = True)

    ### close source
    f.close()

    # clsoe log file
    f_log.close()

### iterate through all JSONs & convert to XML
for path in pathlib.Path(dir_source).iterdir():
    if path.is_file():
        if(path.suffix == '.json'):
            corpo2dracor(path, logfile_path)

print("---end---") # debugging