MY_IP=`curl -s http://whatismyip.akamai.com`
read -p "Enter Host IP address: " -e -i $MY_IP HOST_IP
ALERT_MANAGER_IP=$HOST_IP
MONITORING_DATA=/var/lib/apporbit/monitoring
mkdir -p $MONITORING_DATA
cp alertmanager.yml prometheus.yml alert.rules $MONITORING_DATA
sed -i "s/AO_HOST_IP/$HOST_IP/g" $MONITORING_DATA/prometheus.yml

for path in exporter-collector alert-data prom-data grafana-data; do
    echo "Creating dir: $MONITORING_DATA/$path"
    mkdir -p $MONITORING_DATA/$path
done

# Specific Images
PROM_IMAGE=prom/prometheus:v1.0.1
ALERT_IMAGE=prom/alertmanager:master
GRAF_IMAGE=grafana/grafana:3.1.0
CAD_IMAGE=google/cadvisor:v0.23.2
NODE_IMAGE=prom/node-exporter:0.12.0
CONSUL_IMAGE=jenkin-registry.gsintlab.com/apporbit/consul

docker pull $PROM_IMAGE
docker pull $ALERT_IMAGE
docker pull $GRAF_IMAGE
docker pull $CAD_IMAGE
docker pull $NODE_IMAGE
docker pull $CONSUL_IMAGE

docker run -d -p 8401:8400 -p 8501:8500 -p 8600:53/udp --restart=always --name apporbit-prometheus-consul -h consul $CONSUL_IMAGE -server --bootstrap-expect 1
docker run -d -p 9100:9100 --net="host" --name=apporbit-node-exporter -v $MONITORING_DATA/exporter-collector:/exporter-collector:Z $NODE_IMAGE --collector.textfile.directory="/exporter-collector"
docker run --volume=/:/rootfs:ro --volume=/var/run:/var/run:rw  --volume=/sys:/sys:ro  --volume=/var/lib/docker/:/var/lib/docker:ro  --publish=9101:8080  --detach=true  --name=apporbit-cadvisor --privileged=true $CAD_IMAGE
docker run -d -p 9093:9093 -v $MONITORING_DATA/alertmanager.yml:/alertmanager.yml:Z -v $MONITORING_DATA/alert-data:/alert-data:Z --name=apporbit-alertmanager $ALERT_IMAGE -config.file=/alertmanager.yml -storage.path=/alert-data
docker run -d -p 9090:9090 -v $MONITORING_DATA/prometheus.yml:/etc/prometheus/prometheus.yml:Z -v $MONITORING_DATA/alert.rules:/etc/prometheus/alert.rules:Z -v $MONITORING_DATA/prom-data:/prom-data:Z -v $MONITORING_DATA/targets:/var/lib/apporbit/monitoring/targets:Z --name=apporbit-prometheus $PROM_IMAGE -config.file=/etc/prometheus/prometheus.yml -storage.local.path=/prom-data -alertmanager.url=http://${ALERT_MANAGER_IP}:9093
docker run -d -p 3000:3000 -v $MONITORING_DATA/grafana-data:/var/lib/grafana:Z -e GF_AUTH_ANONYMOUS_ENABLED=true -e GF_AUTH_ANONYMOUS_ORG_ROLE=Admin -e GF_USERS_DEFAULT_THEME=light --name=apporbit-grafana $GRAF_IMAGE
