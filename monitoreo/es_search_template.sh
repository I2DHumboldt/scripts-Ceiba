# Script para crear un Search Template en ElasticSearch de Ceiba
# Se usará desde el portal I2D para acceder a título y abstract de resultados.
# Autor: German Carrillo (gcarrillo@linuxmail.org) para IAvH, abril de 2016

curl -XPOST http://localhost:9200/_search/template/dsl -d '
{
    "template": {
        "size": "{{size}}",
        "from": "{{from}}",
        "query": {
          "query_string": {
            "query": "{{query}}"
          }
        },   
        "_source": ["resource.title", "resource.abstract"]
    }
}
' 
