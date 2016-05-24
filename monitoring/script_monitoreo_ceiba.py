#!/usr/bin/python
"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) for IAvH
    License: GNU GPL v.2.0
"""
import os, glob, csv, datetime, requests
import xml.etree.ElementTree
from script_parse_eml import generateJSONForEML

esURL = 'http://localhost:9200/ceiba/recurso/'
statusFilePath = '/docs/tr/iavh/Ceiba/search/scripts/estado_recursos_ceiba.txt'
basePath = '/docs/tr/iavh/Ceiba/demo_datadir_/resources/'
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
        # Get STATUS from resource.xml
        resourceFile = os.path.join( basePath, folder, 'resource.xml' )
        resourceStatus = "UNKNOWN"
        try:
            parsed = xml.etree.ElementTree.parse( resourceFile )
        except IOError, xml.etree.ElementTree.ParseError:
            print "WARNING: El archivo", resourceFile, "tiene problemas!!!"
        else:
            status = parsed.find('./status')
            if status is not None:
                resourceStatus = status.text
    
        # Save current resource's triple
        dictNewStatus.append( [folder[:-1], latestEML, resourceStatus] )

""" Compare triples [resource_short_name, eml_file_name, resource_status]
    input:  dictCurrentStatus, dictNewStatus 
    output: when updates are identified, trigger JSON generation and ES requests
"""
onlyInCurrent = [triple for triple in dictCurrentStatus if triple not in dictNewStatus]
onlyInNew = [triple for triple in dictNewStatus if triple not in dictCurrentStatus]

dictOnlyInNew = {}
for triple in onlyInNew:
    dictOnlyInNew[triple[0]] = [triple[1], triple[2]]

dictOnlyInCurrent = {}
for triple in onlyInCurrent:
    dictOnlyInCurrent[triple[0]] = [triple[1], triple[2]]

for resource, (eml, status) in dictOnlyInNew.items():
    if resource not in dictOnlyInCurrent:
        # New resource: Generate JSON and index it
        changesPerformed += getTimestamp() + " New resource: " + resource + " (EML: " + eml + ", STATUS: " + status + "), (JSON + index)\n"
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
        # Updated resource: Delete ES doc, generate JSON, and index it
        changesPerformed += getTimestamp() + " Updated resource: " + resource + " (EML: " + eml + ", STATUS: " + status + "), (delete ES doc + JSON + index)\n"    
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

for resource, (eml, status) in dictOnlyInCurrent.items():
    if resource not in dictOnlyInNew:
        # Resource deleted: Delete ES doc
        changesPerformed += getTimestamp() + " Resource deleted: " + resource + " (EML: " + eml + ", STATUS: " + status + "), (delete ES doc)\n"
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

