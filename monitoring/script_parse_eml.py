"""
    Copyright (c) 2016, German Carrillo (gcarrillo@linuxmail.org) for IAvH
    License: GNU GPL v.2.0
"""
import xml.etree.ElementTree, json

typeTranslation = {"occurrence":u"Registro biol\u00f3gico", 
    "metadata-only":"Solamente metadatos", 
    "checklist":"Listado de chequeo", 
    "other":"Otro", # End
    "inventario":"inventario",
    "anfibios":"anfibios",
    "metadata":"Metadatos",
    "sevilla":"Sevilla",
    "magnoliopsida":"magnoliopsida",
    "bosque seco":"bosque seco",
    u"ecoregiones nari\xf1o":u"ecoregiones Nari\xf1o",
    "lista anotada":"lista anotada",
    "piedemonte":"piedemonte",
    "fototrampeo":"fototrampeo",
    "acacia farnesiana":"Acacia farnesiana",
    "colombia":"Colombia", #rrbb_pnn_vocs
    "aves":"aves",
    "plantas":"plantas",
    u"artropofauna ed\xe1fica":u"artropofauna ed\xe1fica",
    "diversidad funcional":"diversidad funcional",
    "tejidos":"Tejidos",
    "frontino":"Frontino",
    u"diversidad flor\xedstica":u"diversidad flor\xedstica",
    "diversidad":"diversidad",
    "tejidos animales":"tejidos animales",
    "amphibia":"Amphibia",
    "hidromedusas":"hidromedusas",
    "fauna de los llanos":"fauna de los llanos",
    "casanare":"casanare",
    u"quir\xf3pteros":u"quir\xf3pteros",
    u"p\xe1ramo":u"p\xe1ramo",
    u"hemidactylus frenatus. hemidactylus angulatus. hemidactylus garnotii. especies introducidas.\ncolombia. relaciones interespec\xedficas.":u"hemidactylus frenatus. hemidactylus angulatus. hemidactylus garnotii. especies introducidas.\ncolombia. relaciones interespec\xedficas.", #biota_v12_n2_05
    "colecciones":"colecciones",
    "lepidoptera":"lepidoptera",
    "herpetofauna":"herpetofauna",
    "andes":"andes",
    "parcela permanente":"parcela permanente",
    "lista de especies":"lista de especies",
    u"centrales hidroel\xe9ctricas":u"centrales hidroel\xe9ctricas",
    "rasgos historia de vida":"rasgos historia de vida",
    "flora":"flora",
    u"categor\xeda de amenaza":u"categor\xeda de amenaza",
    u"levantamientos portuarios de l\xednea base biol\xf3gica":u"levantamientos portuarios de l\xednea base biol\xf3gica",
    "ephemeroptera":"ephemeroptera",
    "belostomatidae":"belostomatidae",
    "bosque de niebla":"bosque de niebla",
    "avifauna":"avifauna",
    u"mam\xedferos":u"mam\xedferos",
    "odc":"odc",
    "bosque seco tropical":"bosque seco tropical",
    "libro rojo":"libro rojo",
    u"occurrence; p\xe1ramo; bosque altoandino; aves; anfibios; tejidos; antioquia; caldas":u"occurrence; p\xe1ramo; bosque altoandino; aves; anfibios; tejidos; antioquia; caldas", #tejidos_frontino_urrao_sonson_uantioquia
    "metadatos":"metadatos",
    "cerambycidae":"cerambycidae",
    "coleoptera":"coleoptera",
    "zapatosa":"zapatosa",
    "aves introducidas":"aves introducidas",
    "polistinae":"polistinae",
    "hymenoptera":"hymenoptera",
    u"zonas \xe1ridas":u"zonas \xe1ridas",
    "batrachoididae":"batrachoididae",
    "peces":"peces",
    "uicn":"uicn",
    "listado de especies":"listado de especies"}
subtypeTranslation = {"taxonomic authority":u"Autoridad Taxon\u00f3mica",  
    "nomenclator authority":"Autoridad Nomenclatural", 
    "inventorythematic":u"Inventario Tem\u00e1tico", 
    "inventoryregional":"Inventario Regional", 
    "global species dataset":"Recurso Mundial de Especies", 
    "derivedfromoccurrence":u"Derivado de Registros Biol\u00f3gicos", 
    "specimen":"Ejemplar", 
    "observation":u"Observaci\u00f3n", # End
    "anfibios":"anfibios",
    u"mam\xedferos":u"mam\xedferos",
    "complejo":"complejo"}


""" Generate JSON file for updated resources
    input:  pathToEML, outPath, idResource
    output: True if JSON was created, False if there were problems
"""
def generateJSONForEML( myFile, outPath, idResource ):
    #basePath = '/docs/tr/iavh/Ceiba/data/20-01-2016/resources/'
    #outPath = '/docs/tr/iavh/Ceiba/search/'
    #myFile = basePath + 'america_exoticas_is_2014/eml-5.xml'

    emlJson = {}

    try:
        parsed = xml.etree.ElementTree.parse( myFile )
    except xml.etree.ElementTree.ParseError:
        print "WARNING: El archivo", myFile, "tiene problemas!!!"
        return False
    else:
        dataset = parsed.find('dataset')
        if dataset is not None:
            emlJson["id"] = idResource # dataset.find( 'alternateIdentifier' ).text.split("r=")[1]

            emlJson["title"] = dataset.find( 'title' ).text
            emlJson["abstract"] = dataset.find( './/abstract/para' ).text.strip().replace("\n"," ")
            
            givenName = dataset.find('.//creator/individualName/givenName')
            surName = dataset.find('.//creator/individualName/surName')
            emlJson["creator"] = (givenName.text if givenName is not None else "") + " " + (surName.text if surName is not None else "")

            givenName = dataset.find('.//metadataProvider/individualName/givenName')
            surName = dataset.find('.//metadataProvider/individualName/surName')
            emlJson["metadataProvider"] = (givenName.text if givenName is not None else "") + " " + (surName.text if surName is not None else "")

            geographicDescription = dataset.find('.//coverage/geographicCoverage/geographicDescription')
            if geographicDescription is not None:
                emlJson["geographicDescription"] = geographicDescription.text
            
            generalTaxonomicCoverage = dataset.find('.//coverage/taxonomicCoverage/generalTaxonomicCoverage')
            if generalTaxonomicCoverage is not None:
                emlJson["generalTaxonomicCoverage"] = generalTaxonomicCoverage.text

            emlJson["taxonRankValue"] = []
            for taxonRankValue in dataset.findall('.//coverage/taxonomicCoverage/taxonomicClassification/taxonRankValue'):
                emlJson["taxonRankValue"].append( taxonRankValue.text )
                
            emlJson["commonName"] = []
            for commonName in dataset.findall('.//coverage/taxonomicCoverage/taxonomicClassification/commonName'):
                for name in commonName.text.split(","):
                    if not name.strip().lower() in emlJson["commonName"] and not name.strip().lower()=="n/a": 
                        emlJson["commonName"].append( name.strip().lower() )

            for keywordSet in dataset.findall( 'keywordSet' ):
                keywordThesaurus = keywordSet.find('keywordThesaurus')
                if keywordThesaurus.text == 'N/A':
                    emlJson["keywords"] = []
                    for keyword in keywordSet.findall('keyword'):
                        emlJson["keywords"].append( keyword.text )
                elif 'type' in keywordThesaurus.text.lower() and not ('subtype' in keywordThesaurus.text.lower()):
                    emlJson["type"] = typeTranslation[keywordSet.find('keyword').text.lower()] if keywordSet.find('keyword').text.lower() in typeTranslation else keywordSet.find('keyword').text # Traducir
                elif 'subtype' in keywordThesaurus.text.lower(): 
                    emlJson["subtype"] = subtypeTranslation[keywordSet.find('keyword').text.lower()] if keywordSet.find('keyword').text.lower() in subtypeTranslation else keywordSet.find('keyword').text # Traducir

            projectTitle = dataset.find('.//project/title')
            if projectTitle is not None:
                emlJson["projectTitle"] = projectTitle.text
                
            funding = dataset.find('.//project/funding/para')
            if funding is not None:
                emlJson["projectFunding"] = funding.text
                
            studyExtent = dataset.find('.//methods/sampling/studyExtent/description/para')
            if studyExtent is not None:
                emlJson["studyExtent"] = studyExtent.text

            rights = dataset.find( 'intellectualRights' )
            if rights is not None:
                emlJson["intellectualRights"] = rights.find('para').text.strip()            
                
        citation = parsed.find('.//additionalMetadata/metadata/gbif/citation')
        if citation is not None:
            emlJson["citation"] = citation.text

        collectionIdentifier = parsed.find('.//additionalMetadata/metadata/gbif/collection/collectionIdentifier')
        if collectionIdentifier is not None:
            emlJson["collectionIdentifier"] = [ e.strip() for e in collectionIdentifier.text.split(",") ]

    resource = {"resource": emlJson}

    #Save to file
    f = open(outPath + emlJson["id"] + ".json", "wt") 
    f.write(json.dumps(resource,ensure_ascii=False,sort_keys=True,indent=3).encode('utf-8'))
    f.close()
    
    return True
