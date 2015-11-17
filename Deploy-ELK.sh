#!/bin/bash

mkdir -p /var/log/apporbit/elk/conf

cat > /var/log/apporbit/elk/conf/logstash.conf << LOGSTASH
input {
  file {
    path => "/var/log/apporbit/stack/*log"
    start_position => "beginning"
  }
  file {
    path => "/var/log/apporbit/stack/mist/*log"
    start_position => "beginning"
  }
  file {
    path => "/var/log/apporbit/platform/passenger.3000.log"
    start_position => "beginning"
  }

}

filter {
    date {
      match => [ "timestamp" , "yyyy-MM-dd HH:mm:ss" ]
    }
}

output {
  elasticsearch { host => "apporbit-elasticsearch" }
  stdout { codec => rubydebug }
}

LOGSTASH

docker rm -f -v apporbit-elasticsearch apporbit-kibana apporbit-logstash
docker run -d --name apporbit-elasticsearch -p 9200:9200 -p 9300:9300 elasticsearch elasticsearch -Des.node.name="GeminiNode"
docker run --name apporbit-kibana --link apporbit-elasticsearch:elasticsearch -p 5601:5601 -d kibana

docker run -d  -v "/var/log/apporbit/elk/conf":/config-dir -v "/var/log/apporbit":/var/log/apporbit --name apporbit-logstash --link  apporbit-elasticsearch:apporbit-elasticsearch logstash logstash -f /config-dir/logstash.conf


