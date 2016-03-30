# Script para definir el mapping de recursos de Ceiba en ElasticSearch
# Autor: Germán Carrillo (gcarrillo@linuxmail.org) for IAvH, marzo de 2016

curl -XPUT http://localhost:9200/ceiba -d '
{
    "settings" : {
        "number_of_shards": 1,    
        "analysis" : {
            "analyzer" : {
                "default" : {
                    "tokenizer" : "standard",
                    "filter" : ["standard", "lowercase", "asciifolding"]
                }
            }
        }
    },
    "mappings": {
        "recurso": {
            "_all": {
                "type": "string",
                "analyzer": "default"
            },
            properties: {
                "abstract": {
                    "type": "string"
                },
                "citation": {
                    "type": "string"
                },
                "collectionIdentifier": {
                    "type": "string"
                },
                "commonName": {
                    "type": "string"
                },
                "creator": {
                    "type": "string"
                },
                "generalTaxonomicCoverage": {
                    "type": "string"
                },
                "geographicDescription": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "intellectualRights": {
                    "type": "string"
                },
                "keywords": {
                    "type": "string"
                },
                "metadataProvider": {
                    "type": "string"
                },
                "projectFunding": {
                    "type": "string"
                },
                "projectTitle": {
                    "type": "string"
                },
                "studyExtent": {
                    "type": "string"
                },
                "subtype": {
                    "type": "string"
                },
                "taxonRankValue": {
                    "type": "string"
                },
                "title": {
                    "type": "string"
                },
                "type": {
                    "type": "string"
                }
            }
        }
    }
}'
