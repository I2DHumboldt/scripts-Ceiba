# Script para crear un Search Template en ElasticSearch de Ceiba
# Se usará desde el portal I2D para acceder a título y abstract de resultados.
# Autor: German Carrillo (gcarrillo@linuxmail.org) para IAvH, abril de 2016

curl -XPOST http://localhost:9200/_search/template/dsl -d '
{
    "template": {
      "size": "{{size}}",
      "from": "{{from}}",
      "query": { 
        "bool": { 
          "must": [
            { "match_phrase": { 
               "_all": {
                   "query":   "{{query}}",
                   "analyzer": "default"
               }
             }}
          ],
          "filter": [ 
            { "term":  { "status": "PUBLIC" }}
          ]
        }
      },
      "_source": ["title", "abstract"]
    }
}
' 
