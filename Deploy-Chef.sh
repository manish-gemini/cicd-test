#!/bin/bash


#### SCRIPT TO DO PRE INSTALLATION STEPS FOR apporbit

## Check if RAM size is 4GB

## Display valid Sys info and see if any value needs to consider for Minimum Requirements

##Docker Run command for Chef
echo "Install Chef or Upgrade Chef"
echo "1) Install Chef"
echo "2) Upgrade Chef"
read -p "Choose Chef Deployment Type from above [2]:" deployType
deployType=${deployType:-2}
if docker ps -a |grep -aq apporbit-chef; then
    docker rm -f apporbit-chef
fi
chef_port=9443
ip=`curl -s http://whatismyip.akamai.com; echo`
printf "Enter the Host IP or Host Name (public resolvable) :"
read -p "Default($ip):" hostip
hostip=${hostip:-$ip}

# Enable the port used by Chef (permanent makes it persist after reboot)
if [ -f /usr/bin/firewall-cmd ]
then
    echo "Adding port '$chef_port' to firewall..."
    firewall-cmd --permanent --add-port=$chef_port/tcp
fi

echo "Setting up iptables rules..."
iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
iptables -D FORWARD -j REJECT --reject-with icmp-host-prohibited
/sbin/service iptables save 

mkdir -p /opt/apporbit/chef-serverkey/

if [ ! -f /opt/apporbit/chef-serverkey/${hostip}.key ] || [ ! -f /opt/apporbit/chef-serverkey/${hostip}.crt ]
then
        echo "1) use existing certificate"
        echo "2) Create a self signed certificate"
        read -p "Enter the type of ssl certificate [Default:2]:" ssltype
        ssltype=${ssltype:-2}
        if [ $ssltype -eq 2 ]
        then
                #Generate SSL Certiticate for https and put it in a volume mount controller location.
                openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=${hostip}" -keyout /opt/apporbit/chef-serverkey/${hostip}.key -out /opt/apporbit/chef-serverkey/${hostip}.crt
        else
                echo "Rename your certificate files as ${hostip}.crt and key as ${hostip}.key"
                read -p "Enter the location where your certificate and key file exist:" sslKeyDir
                if [ ! -d $sslKeyDir ]
                then
                        echo "Dir does not exist, Exiting..."
                        exit
                fi
                cd $sslKeyDir
                if [ ! -f ${hostip}.key ] || [ ! -f ${hostip}.crt ]
                then
                        echo "key and certificate files are missing."
                        echo "Note that key and crt file name should be ${hostip}.key and ${hostip}.crt. Rename your files accordingly and retry."
                        exit
                fi
                cp -f ${hostip}.key /opt/apporbit/chef-serverkey/${hostip}.key
                cp -f ${hostip}.crt /opt/apporbit/chef-serverkey/${hostip}.crt
        fi
fi

echo "Deploy from Local image = 1"
echo "Deploy from internal registry = 2"
read -p "Default(2):" deployType
deployType=${deployType:-2}
echo $deployType

echo "Continue to run chef ..."

if [ $deployType -eq 1 ]
then
  docker run -m 2g -it --restart=always -e UPGRADE=$deployType -p $chef_port:$chef_port -v /opt/apporbit/chef-server:/var/opt/chef-server -v /opt/apporbit/chef-serverkey/:/var/opt/chef-server/nginx/ca/ -v /etc/chef-server/ --name apporbit-chef -h ${hostip} -d apporbit/apporbit-chef
else
  echo "Login to the Internal Registry"
  docker login https://secure-registry.gsintlab.com
  echo "Pull Chef Server from Internal Registry..."
  docker pull secure-registry.gsintlab.com/apporbit/apporbit-chef:1.0
  echo "Please change your chef password by logging into the UI."
  echo "Using hostname: ${hostip}"
  docker run -m 2g -it --restart=always -e UPGRADE=$deployType -p $chef_port:$chef_port -v /opt/apporbit/chef-server:/var/opt/chef-server -v /opt/apporbit/chef-serverkey/:/var/opt/chef-server/nginx/ca/ -v /etc/chef-server/ --name apporbit-chef -h ${hostip} -d secure-registry.gsintlab.com/apporbit/apporbit-chef:1.0
  echo "Please change your chef password by logging into the UI."
fi
