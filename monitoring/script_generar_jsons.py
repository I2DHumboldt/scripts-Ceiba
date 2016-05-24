#!/usr/bin/python
"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) for IAvH
    License: GNU GPL v.2.0
"""

import os, glob
import script_parse_eml

basePath = '/docs/tr/iavh/Ceiba/demo_datadir_/resources/'
outPath = '/docs/tr/iavh/Ceiba/search/emlJSONs/'
statusFilePath = '/docs/tr/iavh/Ceiba/search/scripts/estado_recursos_ceiba.txt'
os.chdir( basePath )

logText = ""

for folder in glob.glob( '**/' ):
    os.chdir( basePath + folder )
    latestEML = None
    emls = [ eml for eml in glob.glob( 'eml*.xml' ) ]
    if len(emls) == 0:
        print "  ### " + folder + " NO tiene EMLs ###" 
    elif len(emls) == 1:
        print folder + " --> " + emls[0] + " (Solo uno)"
        latestEML = emls[0]
    else:
        emls.remove('eml.xml')
        emls.sort(key=lambda x: int(x[4:][:-4]))
        print folder + " --> " + emls[-1]
        latestEML = emls[-1]

    if latestEML:
        script_parse_eml.generateJSONForEML( basePath + folder + latestEML, outPath, folder[:-1] )
        logText += folder[:-1] + "," + latestEML + "\n"
    else:
        print "**************************** PILAS ************************"
    
    if logText:
        with open(statusFilePath, 'wb') as f:
            f.write( logText )
    
