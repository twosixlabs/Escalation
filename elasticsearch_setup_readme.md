docker pull docker.elastic.co/elasticsearch/elasticsearch:7.12.0

docker run --name es_container -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.12.0

# creates index template, writes file of demo data to elasticsearch
python setup_test_elasticsearch.py