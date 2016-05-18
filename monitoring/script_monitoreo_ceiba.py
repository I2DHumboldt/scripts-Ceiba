#!/usr/bin/python
"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) for IAvH
    License: GNU GPL v.2.0
"""
import os, glob, csv, datetime, requests
from script_parse_eml import generateJSONForEML

esURL = 'http://localhost:9200/ceiba/recurso/'
statusFilePath = '/docs/tr/iavh/Ceiba/search/scripts/estado_recursos_ceiba.txt'
basePath = '/docs/tr/iavh/Ceiba/demo_datadir/resources/'
outPath = '/docs/tr/iavh/Ceiba/search/emlJSONs/'
logFilePath = '/docs/tr/iavh/Ceiba/search/scripts/log_monitoreo_ceiba.txt'

changesPerformed = ''

""" Get timestamp to help describe events in a log file """
def getTimestamp():
    return datetime.datetime.now().strftime("%Y %B %d, %A. %I:%M%p")

""" Send requests to ES
    input:  HTTP request (delete and index), delete, or index
"""
def sendHTTPRequestToES( requestType, resource, esURL, pathToJSON=None ):
    global changesPerformed
    if requestType == 'delete':
        try:
            requests.delete( esURL + resource )
        except requests.exceptions.RequestException:
            changesPerformed += getTimestamp() + " ERROR in HTTP request (" + requestType + ") " + esURL + resource + "\n"
    elif requestType == 'index':
        try:
            with open( pathToJSON, 'rb') as jsonFile:
                requests.post( esURL + resource, data=jsonFile )
        except requests.exceptions.RequestException:
            changesPerformed += getTimestamp() + " ERROR in HTTP request (" + requestType + ") " + esURL + resource + "\n"


""" Read file estado_recursos_ceiba.txt 
    input:  statusFilePath  
    output: dictCurrentStatus
"""
with open( statusFilePath, 'r' ) as f:
    dictCurrentStatus = [row for row in csv.reader( f.read().splitlines() )]

""" Read resources and latest emls
    input:  basePath
    output: dictNewStatus
"""
os.chdir( basePath )
dictNewStatus = []

for folder in glob.glob( '**/' ):
    os.chdir( basePath + folder )
    latestEML = None
    emls = [ eml for eml in glob.glob( 'eml*.xml' ) ]

    if len(emls) == 0:
        pass
    elif len(emls) == 1:
        latestEML = emls[0]
    else:
        emls.remove('eml.xml')
        emls.sort(key=lambda x: int(x[4:][:-4]))
        latestEML = emls[-1]

    if latestEML is not None:
        dictNewStatus.append( [folder[:-1], latestEML] )

""" Compare
    input:  dictCurrentStatus, dictNewStatus 
    output: when updates are identified, trigger JSON generation and ES requests
"""
onlyInCurrent = [status for status in dictCurrentStatus if status not in dictNewStatus]
onlyInNew = [status for status in dictNewStatus if status not in dictCurrentStatus]

dictOnlyInNew = {}
for status in onlyInNew:
    dictOnlyInNew[status[0]] = status[1] 

dictOnlyInCurrent = {}
for status in onlyInCurrent:
    dictOnlyInCurrent[status[0]] = status[1] 

for resource, eml in dictOnlyInNew.items():
    if resource not in dictOnlyInCurrent:
        # New resource: Generate JSON and index it
        changesPerformed += getTimestamp() + " New resource: " + resource + ", (JSON + index)\n"
        try:
            jsonForEML = generateJSONForEML( basePath+resource+"/"+eml, outPath, resource )
            if not jsonForEML: 
                changesPerformed += getTimestamp() + " ERROR, EML doesn't seem to be a valid XML. " + eml + " for " + resource + "\n"
        except Exception:
            jsonForEML = False
            changesPerformed += getTimestamp() + " ERROR while parsing EML " + eml + " for " + resource + "\n"
        if jsonForEML: 
            sendHTTPRequestToES( 'index', resource, esURL, outPath+resource+'.json' )
    else:
        # Updated resource: Delete ES doc, generate JSON and index it
        changesPerformed += getTimestamp() + " Updated resource: " + resource + " (EML: " + eml + "), (delete ES doc + JSON + index)\n"    
        sendHTTPRequestToES( 'delete', resource, esURL )
        try:
            jsonForEML = generateJSONForEML( basePath+resource+"/"+eml, outPath, resource )
            if not jsonForEML: 
                changesPerformed += getTimestamp() + " ERROR, EML doesn't seem to be a valid XML. " + eml + " for " + resource + "\n"
        except Exception:
            jsonForEML = False
            changesPerformed += getTimestamp() + " ERROR while parsing EML " + eml + " for " + resource + "\n"
        if jsonForEML:
            sendHTTPRequestToES( 'index', resource, esURL, outPath+resource+'.json' )

for resource, eml in dictOnlyInCurrent.items():
    if resource not in dictOnlyInNew:
        # Resource deleted: Delete ES doc
        changesPerformed += getTimestamp() + " Resource deleted: " + resource + ", (delete ES doc)\n"
        sendHTTPRequestToES( 'delete', resource, esURL )
        

""" Update both estado_recursos_ceiba.txt and log files
    input: (statusFilePath, dictNewStatus), (logFilePath, actions performed + timestamp)
"""
if changesPerformed:
    with open( statusFilePath, 'wb' ) as f:
        # Overwrite the old file with the modified rows
        writer = csv.writer( f )
        writer.writerows( dictNewStatus )

    with open( logFilePath, 'a' ) as log:
        log.write( changesPerformed )   

