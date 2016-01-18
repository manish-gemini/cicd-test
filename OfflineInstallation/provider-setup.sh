#!/bin/bash

AO_RESOURCE_PATH=/opt/apporbit/resources
AO_DOWNLOADS_PATH=/tmp/appOrbitResources.tar
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
    if [ ! -f /etc/yum.repos.d/apporbit.repo ]
    then
        cp apporbit-local.repo /etc/yum.repos.d/
    fi

    echo "Check for Docker Version "
    if exists docker
    then
        echo "Docker exists:" `docker -v` "from" `rpm -qa docker`
    else
        echo "Docker is not installed. Installing docker..."
        #yum -y update
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

function run_offline_container {

    if docker ps -a |grep -aq apporbit-chef; then
        echo "appOrbit Offline Container is already runnning. The container will removed first."
        read -r -p "Do you want to continue?[y/n]" -n 1 -r installChef
        echo    # (optional) move to a new line
        if [[ $installChef =~ ^[Yy]$ ]]
        then
            echo "Removing existing Offline container"
            docker rm -f apporbit-chef
        else
            echo "Exiting without installing Offline Server"
            exit 1
        fi
    fi

    echo -n "Starting apporbit-offline service..."
    docker run --name approbit-offline --restart=always -p 9291:9291 -p 9292:9292 -v $AO_RESOURCE_PATH/appOrbitGems:/opt/rubygems -v $AO_RESOURCE_PATH/appOrbitRPMs:/opt/repos -d apporbit/apporbit-offline
    echo "...[OK]"
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

function main {
    echo -n "Checking Platform Compatibility"
    check_platform
    echo "...[OK]"

    set_selinux

    uncompress_resources

    setup_local_apporbit_repo

    install_docker

    load_offline_container

    run_offline_container
}

main
