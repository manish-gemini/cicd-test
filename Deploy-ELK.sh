#!/bin/bash

mkdir -p /var/log/gemini/elk/conf

cat > /var/log/gemini/elk/conf/logstash.conf << LOGSTASH
input {
  file {
    path => "/var/log/gemini/stack/*log"
    start_position => "beginning"
  }
  file {
    path => "/var/log/gemini/stack/mist/*log"
    start_position => "beginning"
  }
  file {
    path => "/var/log/gemini/platform/passenger.3000.log"
    start_position => "beginning"
  }

}

filter {
    date {
      match => [ "timestamp" , "yyyy-MM-dd HH:mm:ss" ]
    }
}

output {
  elasticsearch { host => "gemini-elasticsearch" }
  stdout { codec => rubydebug }
}

LOGSTASH

docker rm -f -v gemini-elasticsearch gemini-kibana gemini-logstash
docker run -d --name gemini-elasticsearch -p 9200:9200 -p 9300:9300 elasticsearch elasticsearch -Des.node.name="GeminiNode"
docker run --name gemini-kibana --link gemini-elasticsearch:elasticsearch -p 5601:5601 -d kibana

docker run -d  -v "/var/log/gemini/elk/conf":/config-dir -v "/var/log/gemini":/var/log/gemini --name gemini-logstash --link  gemini-elasticsearch:gemini-elasticsearch logstash logstash -f /config-dir/logstash.conf


