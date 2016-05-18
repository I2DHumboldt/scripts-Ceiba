#!/usr/bin/python
"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) para el IAvH
    License: GNU GPL v.2.0
    
    Script to update values of a specific EML element in all Ceiba resources.
    Be careful: It does overwrite all prior versions element values also.
"""
import os, glob
import xml.etree.ElementTree
import csv 

mappingPath = '/home/germap/Desktop/mapeo.csv'
basePath = '/docs/tr/iavh/Ceiba/demo_datadir_/resources/'
xpath = './dataset/intellectualRights/para' #'./dataset/alternateIdentifier'
os.chdir( basePath )
valuesFound = []
uniqueValuesFound = None

# Get mapping dictionary ({"current_value_0":"correct_value_A", "cv1":"cvB", ... })
data = csv.reader(open(mappingPath),delimiter=';')
fields = data.next()
mapping = {}
for row in data:
    mapping[row[0].replace('\xc2\xa0',' ').decode("utf-8")] = row[1].decode("utf-8")
    
print "Mapping read!",len(mapping),"values found."


def getElementValue( file, xpath ):
    try:
        parsed = xml.etree.ElementTree.parse( file )
    except xml.etree.ElementTree.ParseError:
        print "WARNING: El archivo", file, "tiene problemas!!!"
        return None
    else:
        current = parsed.find( xpath )
        if current is not None:
            if current.text.strip() in mapping:
                return mapping[current.text.strip()]
            else: 
                print "WARNING: Value",current.text,"not found in mapping."
                return None
        else:
            print "WARNING: Couldn't find value in",file
            return None 


def updateEML( file, xpath, value ):
    # Parse EML, read the desired element and overwrite it
    try:
        parsed = xml.etree.ElementTree.parse( file )
    except xml.etree.ElementTree.ParseError:
        print "WARNING: El archivo", file, "tiene problemas!!!"
    else:
        current = parsed.find( xpath )
        if current is not None:
            current.text = value
            parsed.write( file )
        else:
            print "WARNING: Couldn't find value in",file



# Iterate through all resources and modify values when necessary
os.chdir( basePath )
noEML = []

for folder in glob.glob( '**/' ): #glob.glob( '**/eml*.xml' )

    os.chdir( basePath + folder )
    emls = [ eml for eml in glob.glob( 'eml*.xml' ) ]
        
    if len(emls) == 0:
    
        noEML.append( folder )
        
    elif len(emls) == 1:
    
        newValue = getElementValue( basePath + folder + emls[0], xpath )
        if newValue:
            updateEML( basePath + folder + emls[0], xpath, newValue )
        else:
            print "New value is None for",folder+emls[0]
        
    else: # Several EMLs found for current resource
    
        emls.remove('eml.xml')
        emls.sort(key=lambda x: int(x[4:][:-4]))

        newValue = getElementValue( basePath + folder + emls[-1], xpath )
        if newValue:
            updateEML( basePath + folder + 'eml.xml', xpath, newValue )
            for eml in emls:
                updateEML( basePath + folder + eml, xpath, newValue )
        else:
            print "New value is None for",folder+emls[-1]


   
print "INFO: # de recursos sin EML:",len(noEML)

