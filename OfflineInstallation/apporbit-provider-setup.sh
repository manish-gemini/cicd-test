#!/bin/bash

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
tmp_dir="$tmp/install.sh.$$"
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

function uncompress_resources {
    CWD=`pwd`
    mkdir -p "$AO_RESOURCE_PATH"
    cd "$AO_RESOURCE_PATH"
    tar -xvf $AO_DOWNLOADS_PATH -C "$AO_RESOURCE_PATH"
    tar -xf $AO_RESOURCE_PATH/appOrbitRPMs.tar.gz
    tar -xf $AO_RESOURCE_PATH/appOrbitGems.tar.gz

    cd $CWD
}

function setup_local_apporbit_repo {
    if [ ! -f /etc/yum.repos.d/apporbit-local.repo ]
    then
        cat <<EOF > /etc/yum.repos.d/apporbit-local.repo
[apporbit-local]
name=appOrbit Repository
baseurl=file://${AO_RESOURCE_PATH}/appOrbitRPMs
enabled=1
gpgcheck=0
EOF
    fi
}


function install_docker {
    echo "Checking Docker Version "
    if exists docker
    then
        echo "Docker exists:" `docker -v` "from" `rpm -qa docker`
    else
        echo "Docker is not installed. Installing docker..."
        yum -y update
        yum -y --disablerepo="*" --enablerepo="apporbit-local" install docker-1.7.1
        systemctl enable docker.service
        systemctl start docker.service
        if ! exists docker
        then
            echo "Docker installation failed. Exiting."
            exit
        fi
    fi

}

function load_offline_container {
    echo -n "Loading apporbit-offline image..."
    docker load < $AO_RESOURCE_PATH/apporbit-offline.tar
    echo "...[OK]"
}

function load_registry_container {
    echo -n "Loading registry container..."
    docker load < $AO_RESOURCE_PATH/registry.tar
    echo "...[OK]"
}

function run_offline_container {

    if docker ps -a |grep -aq apporbit-offline; then
        echo "appOrbit Offline Container is already runnning. The container will removed first."
        read -r -p "Do you want to continue?[y/n]" -n 1 -r installOffline
        echo    # (optional) move to a new line
        if [[ $installOffline =~ ^[Yy]$ ]]
        then
            echo "Removing existing Offline container"
            docker rm -f apporbit-offline
        else
            echo "Exiting without installing Offline Server"
            return 1
        fi
    fi

    echo -n "Starting apporbit-offline service..."
    docker run --name apporbit-offline --restart=always -p 9291:9291 -p 9292:9292 -v $AO_RESOURCE_PATH/appOrbitGems:/opt/rubygems -v $AO_RESOURCE_PATH/appOrbitRPMs:/opt/repos -d apporbit/apporbit-offline
    echo "...[OK]"
}

function run_registry_container {

    if docker ps -a |grep -aq apporbit-registry; then
        echo "appOrbit Registry Container is already runnning. The container will removed first."
        read -r -p "Do you want to continue?[y/n]" -n 1 -r installRegistry
        echo    # (optional) move to a new line
        if [[ $installRegistry =~ ^[Yy]$ ]]
        then
            echo "Removing existing Registry container"
            docker rm -f apporbit-registry
        else
            echo "Exiting without installing Registry Server"
            return 1
        fi
    fi

    echo -n "Starting apporbit-registry service..."
    mkdir -p $AO_RESOURCE_PATH/registry-data
    docker run -d -p 5000:5000 --restart=always --name apporbit-registry -v $AO_RESOURCE_PATH/registry-data:/var/lib/registry registry:2
    echo "...[OK]"
}

function setup_docker_daemon_insecure_reg {
    DOCKER_CONF_PATH=/etc/sysconfig/docker
    grep -q '^INSECURE_REGISTRY' $DOCKER_CONF_PATH && sed -i "s/^INSECURE_REGISTRY.*/INSECURE_REGISTRY='--insecure-registry ${docker_registry_url}'/" $DOCKER_CONF_PATH || echo "INSECURE_REGISTRY='--insecure-registry ${docker_registry_url}'" >> $DOCKER_CONF_PATH
    systemctl restart docker.service
}

function load_infra_containers {
    echo -n "Loading infra images..."
    for k in ${!infra_containers[@]}
    do
        docker load < $AO_RESOURCE_PATH/infra_images/apporbit-$k.tar
    done
    echo "...[OK]"
}

function tag_push_infra_containers {
    echo "Waiting for registry container to come up.."
    until $(curl --output /dev/null --silent --head --fail http://${docker_registry_url}/v2/); do
        printf '.'
        sleep 5
    done
    echo -n "Tagging infra containers..."
    for k in ${!infra_containers[@]}
    do
        docker tag google_containers/$k:${infra_containers[$k]} ${docker_registry_url}/google_containers/$k:${infra_containers[$k]}
        docker push ${docker_registry_url}/google_containers/$k:${infra_containers[$k]}
    done
    echo "...[OK]"
}

function get_host_ip() {
    read -p "Enter IP of this host: " offline_provider_ip
    docker_registry_url=$offline_provider_ip:5000
}

function set_selinux {
    echo "Setting sestatus to permissive"
    response="y"
    read -p "Do you want to continue ? [y]/n : " -r
    echo
    REPLY=${REPLY:-$response}
    if [[ $REPLY =~ ^[Yy] ]]
    then
        setenforce 0
        echo "Successfully set sestatus to permissive";
    else
        echo "SELinux must be set to permissive for running docker container"
        exit;
    fi
}

function show_setup_information() {
    echo
    echo "################################################################################"
    echo "Note down following information for further provisioning."
    echo
    echo "INTERNAL REGISTRY URL: ${docker_registry_url}"
    echo "PROVIDER IP: ${offline_provider_ip}"
    echo
    echo "################################################################################"
}

function main {
    declare -rA infra_containers=(
        [etcd]=2.0.9
        [kube2sky]=1.11
        [skydns]=2015-03-11-001
        [exechealthz]=1.0
        [kube-ui]=v3
        [pause]=0.8.0
    )

    echo -n "Checking Platform Compatibility"
    check_platform
    echo "...[OK]"

    get_host_ip

    set_selinux

    uncompress_resources

    setup_local_apporbit_repo

    install_docker

    load_offline_container

    load_registry_container

    run_offline_container

    run_registry_container

    setup_docker_daemon_insecure_reg

    load_infra_containers

    tag_push_infra_containers

    show_setup_information
}

read -p "Enter path of downloaded archive: " AO_DOWNLOADS_PATH
export AO_DOWNLOADS_PATH=$AO_DOWNLOADS_PATH
read -p "Enter directory path for extracting resources: " AO_RESOURCE_PATH
export AO_RESOURCE_PATH=$AO_RESOURCE_PATH
if [ ! -f  $AO_DOWNLOADS_PATH ]; then
    echo "File not found or unreadable. Exiting.."
    exit 1
fi

main
