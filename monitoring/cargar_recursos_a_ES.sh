# Script para cargar recursos de Ceiba (convertidos en archivos JSON) a Elasticsearch
# Autor: German Carrillo (gcarrillo@linuxmail.org) for IAvH, marzo de 2016
for filename in $( find /docs/tr/iavh/Ceiba/search/emlJSONs/ -name "*.json")
do
echo $filename
fbname=$(basename $filename .json)  #Extract the filename to be used as id
curl -XPOST http://localhost:9200/ceiba/recurso/$fbname --data-binary @$filename
done
