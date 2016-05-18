#!/usr/bin/python
"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) para el IAvH
    License: GNU GPL v.2.0
    
    Script to query all values of a specific EML element in all Ceiba resources. 
    The script can optionally overwrite values from a mapping given as csv. In 
      this case, it would only overwrite the latest EML.         
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


# Get latestEMLs
os.chdir( basePath )
noEML = []
latestEMLs = []
for folder in glob.glob( '**/' ): #glob.glob( '**/eml*.xml' )
    os.chdir( basePath + folder )
    emls = [ eml for eml in glob.glob( 'eml*.xml' ) ]
        
    if len(emls) == 0:
        noEML.append( folder ) #print "  ### " + folder + " NO tiene EMLs ###" 
    elif len(emls) == 1:
        latestEMLs.append( basePath + folder + emls[0] )
        #print folder + " --> " + emls[0] + " (Solo uno)"
    else:
        emls.remove('eml.xml')
        emls.sort(key=lambda x: int(x[4:][:-4]))
        latestEMLs.append( basePath + folder + emls[-1] )
        #print folder + " --> " + emls[-1]

print len(noEML)+len(latestEMLs),"resources:",len(latestEMLs),"EMLs found.", len(noEML),"EMLs NOT found."


# Parse EML, read the desired element and overwrite it
for file in latestEMLs:
    try:
        parsed = xml.etree.ElementTree.parse( file )
    except xml.etree.ElementTree.ParseError:
        print "WARNING: El archivo", file, "tiene problemas!!!"
    else:
        current = parsed.find( xpath )
        if current is not None:
            if current.text.strip() in mapping:
                # Write the new value in the file (uncomment the next 2 lines for it)
                #print "New:",mapping[current.text.strip()]
                #current.text = mapping[current.text.strip()]
                #parsed.write( file )
                pass
            else:
                print "WARNING: ############# Not found #"+current.text+"# ###########"
            valuesFound.append( current.text )
        else:
            print "WARNING: Couldn't find value in",file

uniqueValuesFound = set( valuesFound )
   
print "There are",len(uniqueValuesFound),"unique values in the",len(valuesFound),"values found:"
for value in uniqueValuesFound:
    print " +",value
