# -*- coding : utf8 -*-
from datetime import datetime
import linecache
from typing import Text
import PyPDF2 as pdf
import re as re
import os
from typing import Any # aus dataTools.py
from PyPDF2 import PdfFileReader as reader
import json
from pathlib import Path

def iter_files(folder:str,func:callable=None) -> (list[Any] or None): # dataTools.py
    return_val = []
    files = os.listdir(folder)
    for file in files:
        print(file)
        abs_path= os.path.join(folder,file)
        if os.path.isfile(abs_path):
            if func:
                return_val.append(func(abs_path))
            else:
                with open(file,"r") as f:
                    return_val.append(f.readlines())
    return return_val or None

def text_to_dict(text:str,write_state:bool=False) -> dict[int,list[str]] or None:
    textLineItems = text.split('\n')    
    my_dict = {}
    j = 0
    for i in range(0,len(textLineItems)-1):
        if len(textLineItems[i].split(" ")) <= 2:
            my_dict[j] = [textLineItems[i],textLineItems[i+1].encode("utf-8").decode("utf-8")]
            j += 1
    if not my_dict:
        return None
    if write_state:
        with open("data/test.json","w") as f:
            print("test write")
            f.write(json.dumps(my_dict,indent=4))
    return my_dict

def getFolgeNr_asString(fileName):
# get episode nr as string

    r_pdf = pdf.PdfFileReader(fileName)

    pdf_page1 = r_pdf.getPage(0).extractText()

    lb = re.compile('\n')

    splittedByLb = re.split('\n',pdf_page1)

    folgeNr = ''
    for line in splittedByLb:
        if(line.find('FOLGE ') > -1 ): # [!!!] not that precise => could be problematic
            folgeNr = line.replace('FOLGE ','')
            break

    if(folgeNr == ''):
        folgeNr = 'Sonderfolge'

    return folgeNr

def getSpeakers(fileName):
# get speakers as array

    r_pdf = pdf.PdfFileReader(fileName)

    pdf_page1 = r_pdf.getPage(0).extractText()

    arrSpeakers = []

    splittedByLb = re.split('\n',pdf_page1)

    headerEndReached = False
    lineCounter = 0
    folgeNr = ''
    headerText = ''
    for line in splittedByLb:
        lineCounter = lineCounter + 1
        headerText = headerText + '\r\n' + line
        # if 'FOLGE ' is reached, there won't be any more speakers listed => break loop
        if(line.find('FOLGE ') > -1 ): # mit regex aufhübschen?! => exakteres Matching?!
            headerEndReached = True # BAUSTELLE: wird nicht genutzt?! [!?!] => headerEnd explizit setzen/nutzen?!
            break
        else:
            # is it a name? (first name usually with numbers in front, because of PyPDF2...)
            regexExpr = re.escape('[A-Z]+\s[A-Z]+') # ASCII only
            regex = re.compile(regexExpr)
            result = re.search(regex, line)
            match = re.match(r'[0-9]*[A-Z\s]+[A-Z]$', line) # get speaker
            
            if match:
                match2 = re.search(r'[A-Z\s]+[A-Z]$', match.group(0)) # get string without numbers-prefix => clean name
                result = match2.group(0) # get string

                # --------- # Folge 04...
                if(result=='CHRISTIAN DORSTEN'): 
                    result = 'CHRISTIAN DROSTEN'
                # --------- # Folge 04...

                arrSpeakers.append(result.title()) # make titlecase => make only first letters of words uppercase && append to array of speakers

    return arrSpeakers

def getSpeakersJobs(fileName):
    # returns something like: [["Korinna Hennig","WISSENSCHAFTSREDAKTEURIN, NDR INFO"],["Christian Drosten","VIROLOGE, CHARITE BERLIN"]]
    arrSpeakersJobs = []

    # [insert magic (yes, this is a placeholder)]

    return arrSpeakersJobs

def getTaggedText(fileName):
    # parse text line by line and tag speakers, headlines etc. + extract/add some metadata

    speakers = getSpeakers(fileName) # get speakers mentioned in header
    episode = getFolgeNr_asString(fileName) # get episode nr

    r_pdf = pdf.PdfFileReader(fileName) # read file

    r_pdf_pageCount = r_pdf.getNumPages() # get number of pages
    
    headlines = ''

    cleanText = ''

    # get document creation date
    r_pdf_info = r_pdf.getDocumentInfo() # get document info
    r_pdf_info_crdate = r_pdf_info.get('/CreationDate') # get date
    r_pdf_info_crdate = datetime.strptime(r_pdf_info_crdate.replace("'", ""), "D:%Y%m%d%H%M%S%z") # make human-readable

    speakersText = '' 
    for speaker in speakers:
        speakersText = speakersText + speaker + ';'

    cleanText = cleanText + '[METADATA=' +  '[EPISODE=' + episode + ']' + '[DOCUMENT_CREATIONDATE=' + str(r_pdf_info_crdate) + ']' + '[SPEAKERS=' + speakersText + ']' + ']' # write document info (creation date)

    lineCounterDocument = 0 # document-wide count of lines
    previousLineWasUpper = '' # store line, if upper case (might be a headline)
    inHeader = True # used to discriminate between header (first lines with list of speakers && episode nr) and body of document

    previousLineState = -1 # -1=freshly initialized; 1=speaker line; 2=speech line

    for pageNr in range(0, r_pdf_pageCount): # iterate through all pages
        cleanText = cleanText + '\n' + '\n' +  '[PAGENR=' + str(pageNr+1) +']' + '\n' + '\n' # write page number

        pdf_page1 = r_pdf.getPage(pageNr).extractText() # get page's text

        splittedByLb = re.split('\n',pdf_page1) # split by linebreak/newline

        lineCounterPage = 0
        
        for line in splittedByLb:
            lineCounterDocument = lineCounterDocument + 1
            lineCounterPage = lineCounterPage + 1 # page-wide count of lines

            # wrap/catch original page count ...
            if(lineCounterPage==1): #first line usually contains something like "1/7" (page counter of pdf)
                line = re.sub(r'(\d+)/(\d+)', r'[PP]\1/\1[/PP]', line)
            
            # check if this is a speaker line
            speakerIndex = -1 # initialize with -1 for not-a-speaker-case, see below
            for i in range(0, len(speakers)):
                #if(speakers[i] == line): # check if ==
                line_len = len(line)
                speaker = speakers[i]
                speaker_len = len(speaker)
                line_rplcspkr = line.replace(speaker,'')
                line_rplcspkr_len = len(line_rplcspkr)

                # instead of only "if(speakers[i] == line):" 
                if(line_len >= speaker_len): 
                    if((speaker == line) or (line_rplcspkr_len == 1)):
                        speakerIndex = i
                        break           

            # maybe do something with this line...
            if(speakerIndex > -1):
                # this line is a speaker line
                if(inHeader == False): # => if in header, do nothing
                    if(previousLineState==2): # new speaker line marks turn => marks end of speech
                        cleanText = cleanText + '\n' + '[/SPEECH]' # mark end of speech                 
                        cleanText = cleanText + '\n' + '\n' + line.replace(speakers[speakerIndex],'[SPEAKER=' + speakers[speakerIndex] + ']')
                        previousLineState = 1 # # -1=freshly initialized; 1=speaker line; 2=speech line

                    if(previousLineState==-1): # very first speaker line
                        cleanText = cleanText + '\n' + '\n' + line.replace(speakers[speakerIndex],'[SPEAKER=' + speakers[speakerIndex] + ']')
                        previousLineState = 1 # # -1=freshly initialized; 1=speaker line; 2=speech line
            else:
                # other lines

                if(lineCounterDocument==1): # very first line of document => mark start of script header
                    cleanText = cleanText + '\n' + '[HEADER]' # mark as start of header

                if(inHeader==False): # => if in header, do nothing
                    if(previousLineState==1): # previous line was a speaker line
                        cleanText = cleanText + '\n' + '[SPEECH]' # mark as start of speech
                        previousLineState = 2 # # -1=freshly initialized; 1=speaker line; 2=speech line
                
                if(line.isupper()): # uppercase => headline?
                    if(inHeader==False): # header stuff isn't headline stuff
                        if(line=='WEITERE INFORMATIONEN'): # == famous last words => end of document
                            cleanText = cleanText + '\n' + '[/SPEECH]' # mark as end of speech
                        if(line.endswith('[/PP]')): # if it's just the original page counter
                            cleanText = cleanText + '\n' + line # just copy
                        if(line.endswith('SARS-2.')): # special case for 230.pdf (yes... D:) [!?!]
                            cleanText = cleanText + '\n' + line # just copy
                        else:
                            #cleanText = cleanText + '\n' + '[UPPER]' + line + '[/UPPER]' # mark upper case line
                            previousLineWasUpper = previousLineWasUpper + line # append to previous line
                    else: # header usually contains uppercase lines
                        cleanText = cleanText + '\n' + line # => just copy the line

                else: # not uppercase
                    cleanText = cleanText + '\n' + line # => just copy the line
                    if(previousLineWasUpper != ''): # if buffer isn't empty
                        headlines = headlines + '[' + previousLineWasUpper + ']' # save contents from buffer
                        previousLineWasUpper = '' # clear buffer

                if(line.find('FOLGE ') > -1 ): # "FOLGE 01 " or "SONDERFOLGE " usually [!?] marks end of header [BAUSTELLE: mit regex aufhübschen?! => exakteres Matching?!] [BAUSTELLE: deckt das wirklich alle Fälle ab?!]
                    cleanText = cleanText + '\n' + '[/HEADER]' # mark end of header
                    inHeader = False # leaving the header

    cleanText = cleanText + '\n\n' + '[HEADLINES=' + headlines + ']' # append headlines at the end of text
    return cleanText

def getCleanText(text):
    # do some clean-up

    cleanText = ''

    text0 = text

    # [PAGENR=...]
    expPAGENR = re.compile(r'\[PAGENR=\d\]')
    text0 = re.sub(expPAGENR,' ',text0)

    # [PP]...[/PP]
    expPP = re.compile(r'\[PP\]\d/\d\[/PP\]')
    text0 = re.sub(expPP,' ',text0)

    # Bindestrich entfernen
    expHyphon = re.compile("\n-")
    text0 = expHyphon.sub('',text0)

    # Zeilenumsprung entfernen
    expLB = re.compile('\n')
    #text0 = expLB.sub(' ',text0)

    # doppelte Leerzeichen entfernen
    expDspace = re.compile('  ')
    text0 = expDspace.sub(' ',text0)
    text0 = expDspace.sub(' ',text0)

    # Sonderzeichen entfernen/ersetzen
    expSpecChar1 = re.compile('Š')
    text0 = expSpecChar1.sub('—',text0)

    """ 
    # [UPPER]...[/UPPER]
    expUPPER = re.compile(r'\[UPPER\][A-Z\s-]*\[/UPPER\]')
    text0 = re.sub(expUPPER,' ',text0)
    """

    cleanText = text0 # this should always be the last result ;)

    return cleanText

def getJSON(path):

    # regex patterns
    expSpeaker = re.compile(r'(\[SPEAKER=)')
    expSpeechStart = re.compile(r'(\[SPEECH\])')
    expSpeechEnd = re.compile(r'(\[/SPEECH\])')
    expHeadlines = re.compile(r'(\[HEADLINES=)')
    expMeta = re.compile(r'(\[METADATA=)')

    expMatchSpeaker = re.compile(r'([A-Z][a-z]+\s)+([A-Z][a-z]+)')
    expMatchEpisode = re.compile(r'((\[EPISODE=)\d*\])')
    #expMatchEpisodeOnly = re.compile(r'\d*') # but why doesn't this catch the digits?!
    expMatchEpisodeOnly = re.compile(r'\[EPISODE=(\d*)\]') # this works though
    expMatchCreationdate = re.compile(r'(\[DOCUMENT_CREATIONDATE=[^\]]*\])') #[DOCUMENT_CREATIONDATE=
    expMatchCreationdateOnly = re.compile(r'([\d]{4}-[\d]{2}-[\d]{2})')
    expMatchCreationdateOnlyGroups = re.compile(r'\d*')

    # this is of 03.03.2022, might change some day
    sourceBase = 'https://www.ndr.de/nachrichten/info/'

    # dict structure
    jsonish = {
            'metadata': {
                'id': '',
                'source': '',
                'title': '',
                'date': {
                    'year': '',
                    'month': '',
                    'day': '',
                    'time': ''
                },
                'speakers': [
                    'Christian Drosten',
                    'Korinna Hennig'
                ]
            },
            'content': {},
            'headlines': []
        }

    content = {}

    # initialize variables
    inSpeech = False
    lineCounter = 0
    spCounter = 0
    speechBuffer = ''
    headlines = []
    speakers = []
    episode = ''
    dateYear = -1
    dateMonth = -1
    dateDay = -1

    filename_woext = get_file_name_prefix(path) # get file name without extension (and without whole path)
    source = sourceBase + filename_woext + '.pdf' # construct source => something like "https://www.ndr.de/nachrichten/info/coronaskript110.pdf"

    f = open(path, 'r', encoding='utf-8') # open txt file
    text = f.read() # read in text

    splittedByLb = re.split('\n',text) # split by linebreak/newline
    for line in splittedByLb: # parse line by line
        lineCounter = lineCounter + 1 # count lines

        if(re.search(expMeta,line)): # search for metadata ([METADATA=...)
            
            # get episode
            match = re.search(expMatchEpisode,line)
            if(match): 
                match2 = re.search(expMatchEpisodeOnly,match.group(0)) # get digits = episode number
                episode = match2.group(1) # got episode number
            else:
                episode = 'missing'

            # get date
            match = re.search(expMatchCreationdate,line)
            if(match): 
                match2 = re.search(expMatchCreationdateOnly,match.group(0)) # get creation date only
                #match3 = re.search(expMatchCreationdateOnlyGroups,match2.group(0)) # get YYYY-MM-DD
                dt = datetime.strptime(match2.group(0), '%Y-%m-%d') # convert to datetime
                dateYear=dt.year
                dateMonth=dt.month
                dateDay=dt.day

        if(re.search(expSpeaker,line)): # search for speaker line ([SPEAKER=...)
            spCounter = spCounter + 1 # count speakers (this later becomes the key for key:value pair)
            match = re.search(expMatchSpeaker,line) # get the speaker's name
            speaker = match.group(0) # [!!!] this might become buggy, if no speaker name was tagged [!!!] => left here on purpose to find tagging errors, you're welcome ;)
            if(not(any(ele in speaker for ele in speakers))): # add speaker to list of speakers, if not yet added
                speakers.append(speaker) # add to to list
            key = spCounter # key for key:value in dict when speech is fully caught

        if(inSpeech): # there was a [SPEECH] above
            if(re.search(expSpeechEnd,line)): # look if it's the end of the speech ([/SPEECH])
                value = [speaker,speechBuffer] # write speaker + speech into value
                speechBuffer = '' # clear buffer
                content.update({key:value}) # write into dict
                inSpeech = False # no more speech here, go on
            else: 
                speechBuffer = speechBuffer + line # it's not => buffer line
        
        if(re.search(expSpeechStart,line)): # found a [SPEECH] tag
            inSpeech = True # it's true!

        if(re.search(expHeadlines,line)): # search for headlines line (should be the last line in the txt) ([HEADLINES=...)
            # build into array-ish structure/string
            line = line.replace('HEADLINES=','')
            line = line.replace(']]',']')
            line = line.replace('][',',')
            line = line.replace('[','')
            line = line.replace(']','')
            # split by delimiter "," && append to array
            for hl in line.split(','):
                headlines.append(hl)
        
    # insert findings into dict
    jsonish['metadata']['id'] = episode # insert source into dict
    jsonish['metadata']['source'] = source # insert source into dict
    jsonish['metadata']['speakers'] = speakers # insert speakers into dict
    jsonish['metadata']['date']['year'] = str(dateYear)
    jsonish['metadata']['date']['month'] = str(dateMonth)
    jsonish['metadata']['date']['day'] = str(dateDay)
    jsonish['content'] = content # insert content into dict
    jsonish['headlines'] = headlines # insert headlines into dict

    return jsonish

def get_file_name_prefix(file_path): #https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python (02.03.2022, leicht abgeändert/debugged)
    basename = os.path.basename(file_path)

    file_name_prefix_match = re.compile(r'^(?P<file_name_prefix>.*)\..*$').match(basename)

    if file_name_prefix_match is None:
        return basename
    else:
        return file_name_prefix_match.group("file_name_prefix")

def iterateFiles(filepath:str):
    debug = 1 # [debug] scrappy debug mode (switch see below)=> process only 1

    directory = os.fsencode(filepath) # get directory as...directory
    for file in os.listdir(directory): # iterate through files in directory
        if(debug == 1): # [debug]
            #debug = debug + 1 # [debug] on/off (comment out == debug off)
            filename = os.fsdecode(file) # get filename
            if filename.endswith(".pdf"): # only take .pdf
                path = os.path.join(filepath,filename) # recreate path
                taggedText = getTaggedText(path) # tagged using [IMATAG=...] and [IMANOTHERTAG]...[/IMANOTHERTAG]
                cleanedText = getCleanText(taggedText) # regex for some cleaning ("\n-" and similar)
                retext = cleanedText # ... legacy for inserting additional steps
                path2 = os.path.join('data','json') # target directory
                index_of_dot = filename.index('.') # get rid of extension
                filename_woext = filename[:index_of_dot] # get rid of extension II
                if os.path.exists(path2):
                    path3 = os.path.join(path2,filename_woext + '.txt')
                    with open(path3,'w',encoding='utf-8') as f:
                        f.write(retext) # write txt
                    jsonishText = getJSON(path3) # parse into json format
                    with open(os.path.join(path2,filename_woext + '.json'),"w") as f:
                        json.dump(jsonishText,f,indent=4) # dump json
                continue
            else:
                print('Datei nicht gefunden: ' + filename)
                continue

# wenn die Python-Datei ausgeführt wird, wird folgendes ausgeführt : 
if __name__ == "__main__":
    # get folder:
    folder = os.path.join('data','pdf')
    # get file count in folder
    file_count = len(os.listdir(folder))-1 # [?] not needed anymore?

    # Iterate over all files in folder:
    iterateFiles(folder)
