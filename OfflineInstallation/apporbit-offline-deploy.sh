#!/bin/bash

_LOG_LEVEL_="DEBUG"
############
# This section has some helper functions to make life easier.
#
# Outputs:
# $tmp_dir: secure-ish temp directory that can be used during installation.
############

# Check whether a command exists - returns 0 if it does, 1 if it does not
exists() {
    if command -v $1 >/dev/null 2>&1
    then
        return 0
    else
        return 1
    fi
}

if test "x$TMPDIR" = "x"; then
    tmp="/tmp"
else
    tmp=$TMPDIR
fi
# secure-ish temp dir creation without having mktemp available (DDoS-able but not expliotable)
tmp_dir="$tmp/install.sh.apporbit"
(umask 077 && mkdir $tmp_dir) || exit 1

############
# end of helpers
############

############
# This section performs platform detection
#
# Outputs:
# $platform: Name of the platform.
# $platform_version: Version of the platform.
# $machine: System's architecture.
############

function check_platform {
    machine=`uname -m`
    os=`uname -s`

    if test -f "/etc/redhat-release"; then
        if test -f "/etc/os-release"; then
            platform_id=`awk -F= '/ID="[a-z]*"/{print $2}' /etc/os-release | tr -d '"'`
        fi
        platform=`sed 's/^\(.\+\) release.*/\1/' /etc/redhat-release | tr '[A-Z]' '[a-z]'`
        platform_version=`sed 's/^.\+ release \([.0-9]\+\).*/\1/' /etc/redhat-release`
        major_version=`echo $platform_version | cut -d. -f1`
        if [ $major_version -lt 7 ]; then
            echo "Unsupported platform version. Please use CentOS/Redhat 7 or later."
            exit 1
        fi
    else
        echo "Incompatible platform! Only CentOS and RedHat supported at the moment."
        exit 1
    fi
}

function get_internal_apporibit_repo_uri {
    read -p "Enter IP of internal repo host : " offline_provider_ip

    internal_repo="http://${offline_provider_ip}:9291/repos/"
    internal_gems_repo="http://${offline_provider_ip}:9292"

    if curl -Is ${internal_repo} | head -1 | grep 200; then
        echo "Verified connection with the repos... OK"
    else
        echo "Unable to connect repositories. Check Network settings and enable connection to  ${internal_repo} "
        exit
    fi

}

function setup_internal_apporbit_repo {
    if [ ! -f /etc/yum.repos.d/apporbit-offline.repo ]
    then
        cat <<EOF > /etc/yum.repos.d/apporbit-offline.repo
[apporbit-offline]
name=appOrbit Repository
baseurl=${internal_repo}
enabled=1
gpgcheck=0
EOF
    fi
}

function set_selinux_settings {
    echo "Installing appOrbit  containers requires selinux to be turned off."
    response="y"
    read -p "Do you want to continue ? [y]/n : " -r
    echo
    REPLY=${REPLY:-$response}
    if [[ $REPLY =~ ^[Yy] ]]
    then
        setenforce 0
        echo "successfully set sestatus to permissive";
    else
        echo "SELinux is currently on.1 sestatus must be set to permissive for deployment. Exiting"
        exit;
    fi
}

function setup_ntp {
    rpm -q ntp
    if [ $? -ne 0 ]
    then
        yum install -y ntp
    fi
    echo "Time will be synchronized with time.nist.gov for this host"
    # TODO: Ask user for ntp server and use it
    ntpdate -b -u time.nist.gov
    echo "...."
}

function install_docker {
    echo "Checking Docker Version "
    if exists docker
    then
        echo "Docker exists:" `docker -v` "from" `rpm -qa docker`
    else
        echo "Docker is not installed. Installing docker..."
        if [ "x$platform_id" == "xcentos" ]; then
            yum -y update
        fi
        # BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1294128
        yum -y --disablerepo="*" --enablerepo="apporbit-offline" upgrade lvm2
        yum -y --disablerepo="*" --enablerepo="apporbit-offline" install docker-1.7.1
        systemctl enable docker.service
        systemctl start docker.service
        if ! exists docker
        then
            echo "Docker installation failed. Exiting."
            exit
        fi
    fi
}

function setup_iptables {
    echo "Setting up iptables rules..."
    iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
    iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited
}

function uncompress_resources {
    CWD=`pwd`
    cd $tmp_dir
    echo "Enter path to Packages tar"
    read -p "Default(${PWD}/appOrbitPackages.tar.gz): " packages_path
    packages_path=${packages_path:-${PWD}/appOrbitPackages.tar.gz}
    if [ ! -f $packages_path ]; then
        echo "Path does not exist. Exiting.."
        exit
    fi
    tar -xvf $packages_path -C $tmp_dir
    cd $CWD
}

function deploy_chef {
    read -p "Do you want to run Configuration Manager in the same machine? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Installing Configuration Manager..."
        chef_port=9443

        # Enable the port used by Chef (permanent makes it persist after reboot)
        if [ -f /usr/bin/firewall-cmd ]
        then
            echo "Adding port '$chef_port' to firewall..."
            firewall-cmd --permanent --add-port=$chef_port/tcp
            /sbin/service iptables save
        fi

        echo "Loading Chef Server..."
        docker load < $tmp_dir/appOrbitPackages/apporbit-chef.tar

        if docker ps -a |grep -aq apporbit-chef; then
            echo "apporbit Chef Container is already runnning."
            echo "Do you want clean setup or upgrade?"
            echo "1. Clean"
            echo "2. Upgrade(default)"
            read -r -p "Enter your choice: " -n 1 -r chef_choice
            chef_choice=${chef_choice:-2}
            if [[ $chef_choice -eq 1 ]]
            then
                echo "Removing Chef container..."
                docker rm -f apporbit-chef
                echo "Cleaning Chef data..."
                rm -rf /opt/apporbit/chef-server /opt/apporbit/chef-serverkey
            fi
        fi
        read -r -p "Enter internal ip of this host: " -r internal_ip
        echo "Starting Chef service.."
        docker run -m 2g -it --restart=always -p $chef_port:$chef_port -v /opt/apporbit/chef-server:/var/opt/chef-server:Z  -v /opt/apporbit/chef-serverkey/:/var/opt/chef-server/nginx/ca/:Z -v /etc/chef-server/ --name apporbit-chef -h $internal_ip -d apporbit/apporbit-chef:2.0
    fi
}

function set_config_info {
    email_id="admin@apporbit.com"
    EMAILID=$email_id
    onPremMode=true

    read -p "Enter the User Email id for On Prem Deployment. Default($email_id):" emailID
    EMAILID=${emailID:-$email_id}

    if [ -z "$theme" ];
    then
        theme="apporbit-v2"
        themeName="apporbit-v2"
    else
        echo "theme is set to '$theme'";
    fi
    versionName="v2"
    OFFLINE_MODE=true
}

function set_passenger_config {
    echo "Max pool Size"
    B=1024
    KB=$((B * B))
    nvcpu=`nproc`
    ramkb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    ramgb=$(((ramkb+(KB-1))/KB))
    RAM_PER_PROCESS=$(((ramgb+(nvcpu-1))/nvcpu))
    echo "RAM_PER_PROCESS: " $RAM_PER_PROCESS
    adjvar1=75
    adjvar2=100
    if [ $RAM_PER_PROCESS = 0 ]
    then
        RAM_PER_PROCESS=1
    fi
    max_app_processes=$(((ramgb*adjvar1)/(RAM_PER_PROCESS*adjvar2)))
    if [ $max_app_processes = 0 ]
    then
        max_app_processes=1
    fi

}

function setup_logrotate {
    if [ ! -f /etc/logrotate.d/apporbitLogRotate ]
    then
        echo "/var/log/apporbit/controller/*log /var/log/apporbit/services/*log {
          daily
          missingok
          size 50M
          rotate 20
          compress
          copytruncate
        }" > /etc/logrotate.d/apporbitLogRotate
    fi
}

function get_host_ip {
    read -p "Enter the Host IP: " hostip
    if [ -z $hostip ]
    then
        echo "Host IP is Mandatory.. Exiting.."
        exit
    fi

}
function generate_ssl_certs {
    if [ ! -f /var/lib/apporbit/sslkeystore/apporbitserver.key ] || [ ! -f /var/lib/apporbit/sslkeystore/apporbitserver.crt ]
    then
        echo "1) use existing certificate"
        echo "2) Create a self signed certificate"
        read -p "Enter the type of ssl certificate [Default:2]:" ssltype
        ssltype=${ssltype:-2}
        if [ $ssltype -eq 2 ]
        then
            #Generate SSL Certiticate for https and put it in a volume mount controller location.
            openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" -keyout /var/lib/apporbit/sslkeystore/apporbitserver.key -out /var/lib/apporbit/sslkeystore/apporbitserver.crt
        else
            echo "Rename your certificate files as apporbitserver.crt and key as apporbitserver.key"
            read -p "Enter the location where your certificate and key file exist:" sslKeyDir
            if [ ! -d $sslKeyDir ]
            then
                echo "Dir does not exist, Exiting..."
                exit
            fi
            cd $sslKeyDir
            if [ ! -f apporbitserver.key ] || [ ! -f apporbitserver.crt ]
            then
                echo "key and certificate files are missing."
                echo "Note that key and crt file name should be apporbitserver.key and apporbitserver.crt. Rename your files accordingly and retry."
                exit
            fi
            cp -f apporbitserver.key /var/lib/apporbit/sslkeystore/apporbitserver.key
            cp -f apporbitserver.crt /var/lib/apporbit/sslkeystore/apporbitserver.crt
        fi
    fi
}

function clean_setup_maybe {
    echo "Do you want to clean up the setup (removes db, Rabbitmq Data etc.,) ?"
    echo "press 1 to clean the setup."
    echo "press 2 to retain the older entries.."
    read -p "Default(2):" cleanSetup
    cleanSetup=${cleanSetup:-2}
    echo $cleanSetup

    if [ $cleanSetup -eq 1 ]
    then
        rm -rf "/var/dbstore"
        rm -rf "/var/lib/apporbit/"
        rm -rf "/var/log/apporbit/"
    fi

    mkdir -p "/var/dbstore"
    mkdir -p "/var/log/apporbit/controller"
    mkdir -p "/var/log/apporbit/services"
    mkdir -p "/var/lib/apporbit/sshKey_root"
    mkdir -p "/var/lib/apporbit/sslkeystore"
    mkdir -p "/opt/apporbit/chef-server"
    mkdir -p "/opt/apporbit/chef-serverkey"

    chcon -Rt svirt_sandbox_file_t /var/dbstore
    chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sshKey_root
    chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sslkeystore
    chcon -Rt svirt_sandbox_file_t /var/log/apporbit/services
    chcon -Rt svirt_sandbox_file_t /var/log/apporbit/controller

}

function remove_conflicting_containers {
    echo "Removing if any existing docker containers with same name to avoid conflicts"

    if docker ps -a |grep -aq apporbit-services;
    then
        docker rm -f apporbit-services
    fi

    if docker ps -a |grep -aq apporbit-controller;
    then
        docker rm -f apporbit-controller
    fi

    if docker ps -a |grep -aq db;
    then
        docker rm -f db
    fi

    if docker ps -a |grep -a apporbit-rmq; then
        docker rm -f apporbit-rmq
    fi

    if docker ps -a | grep -a apporbit-docs; then
        docker rm -f apporbit-docs
    fi
}

function load_containers {

    CWD=`pwd`
    cd $tmp_dir/appOrbitPackages/

    echo "Loading Platform... "
    docker load < apporbit-controller.tar
    echo "Loading Stack..."
    docker load < apporbit-services.tar
    echo "Loading Mysql..."
    docker load < mysql.tar
    echo "Loading RMQ..."
    docker load < apporbit-rmq.tar
    echo "Loading Docs..."
    docker load < apporbit-docs.tar

    cd $CWD
}

function start_services {
    echo "Starting DB.."
    docker run --name db --restart=always -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24
    echo "Sleeping for 60 seconds"
    sleep 60
    docker run -m 2g -d --hostname rmq  --name apporbit-rmq --restart=always -d apporbit/apporbit-rmq
    docker run --name apporbit-docs --restart=always -p 9080:80 -d apporbit/apporbit-docs
    echo "apporbit services run..."
    if docker ps -a |grep -aq apporbit-chef; then
        docker run -t --name apporbit-services -e GEMINI_INT_REPO=${internal_repo} -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 -e OFFLINE_MODE=$OFFLINE_MODE --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit --volumes-from apporbit-chef -d apporbit/apporbit-services
        echo "controller run ..."
        docker run -t --name apporbit-controller -p 80:80 -p 443:443  -e GEMINI_INT_REPO=${internal_repo} -e LOG_LEVEL=$_LOG_LEVEL_ -e ONPREM_EMAIL_ID=$EMAILID -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName -e CURRENT_API_VERSION=$versionName -e OFFLINE_MODE=$OFFLINE_MODE --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d apporbit/apporbit-controller
    else
        docker run -t --name apporbit-services -e GEMINI_INT_REPO=${internal_repo} -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 -e OFFLINE_MODE=$OFFLINE_MODE --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/services:/var/log/apporbit  -v /var/lib/apporbit/sshKey_root:/root -d apporbit/apporbit-services
        echo "controller run ..."
        docker run -t --name apporbit-controller -p 80:80 -p 443:443 -e GEMINI_INT_REPO=${internal_repo} -e LOG_LEVEL=$_LOG_LEVEL_ -e ONPREM_EMAIL_ID=$EMAILID -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName -e CURRENT_API_VERSION=$versionName -e OFFLINE_MODE=$OFFLINE_MODE  --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d apporbit/apporbit-controller
    fi

}

function main {
    echo -n "Checking Platform Compatibility"
    check_platform
    echo "...[OK]"

    get_internal_apporibit_repo_uri

    setup_internal_apporbit_repo

    set_selinux_settings

    install_docker

    setup_iptables

    uncompress_resources

    deploy_chef

    set_config_info

    set_passenger_config

    setup_logrotate

    clean_setup_maybe

    generate_ssl_certs

    get_host_ip

    load_containers

    remove_conflicting_containers

    start_services
}

main
