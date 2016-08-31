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

# Check Internet Connectivity

function check_internet {
    if ! ping -c 2 -w 2 -W 1 -q 8.8.8.8 >/dev/null 2>&1;
    then
        echo 'Unable to reach Internet, Exiting..'
        exit 1
    fi

    if ! ping -c 2 -w 2 -W 1 -q google.com >/dev/null 2>&1;
    then
        echo "Unable to reach google.com"
        if [ $? -eq 2 ]; then
            echo 'DNS resolution failed, check DNS settings. Exiting..'
        fi
        exit 1
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

function get_internal_registry {
    echo "Enter url of registry(without https://)"
    read -p "Default(https://offline-registry.gsintlab.com): " internal_registry_url
    export INTERNAL_REGISTRY=${internal_registry_url:-offline-registry.gsintlab.com}
}

function install_docker {
    docker_version="1.10.3"
    docker_lower_bound="1.7.1"

    cp Dockerfiles/apporbit.repo /etc/yum.repos.d/

    echo "Check for Docker Version "
    if exists docker
    then
        ## checking for installed docker version
        installed_version=$(docker -v | awk '{print $3}'|sed 's/,//g')
        ## checking for the docker version needs to upgrade or not with latest supported by apporbit
        upgrade_version=$(echo -ne "${docker_version}\n${installed_version}" |sort -Vr| head -n1)
        ## comparing the installed docker version and supported by the apporbit
        ## older docker version will be for upgraded
        if [ ${installed_version} == ${docker_version} ]; then
            echo "Expected docker version exists:" $(docker -v) "from" $(rpm -qa docker)
        elif [ ${upgrade_version} == ${docker_version} ]; then
            echo "Older docker version ${installed_version}, expected docker ${docker_version}"
            read -p "Do you want to upgrade with docker-${docker_version} [ y ] :" user_input
            user_input=${user_input:-y}
            if [ ${user_input} == 'y' ];then
                yum -y install docker-${docker_version}
                if [ $? -eq 0 ];then
                   echo "Docker upgraded to docker-${docker_version}"
                else
                   echo "Failed to upgrade, Exiting."
                   exit 1
                fi
                ## docker daemon --log-driver flag enabled
                 if grep -q "log-driver=journald" /etc/sysconfig/docker; then
                    sed -i 's/log-driver=journald/log-driver=json-file/' /etc/sysconfig/docker
                    systemctl restart docker.service
                fi
            else
                echo "WARNING: running older docker version ${installed_version} , Apporbit supports docker ${docker_version}"
                ## checking if the older version support by apporbit
                ## comparing the installed version with lower bound docker version supported by apporbit
                upgrade_old_version=$(echo -ne "${docker_lower_bound}\n${installed_version}" |sort -Vr| head -n1)
                if [ ${upgrade_old_version} == ${docker_lower_bound} ];then
                  echo "WARNING: Apporbit supports docker-${docker_version}, you need to upgrade."
                else
                  echo "FAILED - Unsupported docker version"
                  echo "Apporbit supports docker version from ${docker_lower_bound} to ${docker_version}"
                  echo "Exiting."
                  exit 1
                fi
            fi
        else
            echo "FAILED - Unsupported docker version"
            echo "Apporbit supports docker version from ${docker_lower_bound} to ${docker_version}"
            echo "Exiting."
            exit 1
        fi
    else
        echo "Docker is not installed. Installing docker..."
        if [ "x$platform_id" == "xcentos" ]; then
            yum -y update
        fi
        # BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1294128
        yum -y upgrade lvm2
        yum -y install docker-${docker_version}
        ## docker daemon --log-driver flag enabled
        if grep -q "log-driver=journald" /etc/sysconfig/docker; then
              sed -i 's/log-driver=journald/log-driver=json-file/' /etc/sysconfig/docker
        fi
        systemctl enable docker.service
        systemctl start docker.service
        if ! exists docker
        then
            echo "Docker installation failed. Exiting."
            exit
        fi
    fi

    # Login to secure registry
    docker login https://${INTERNAL_REGISTRY}


}

function download_images {

    echo "Downloading CentOS..."
    docker pull centos:centos7.0.1406
    echo "Downloading MySQL..."
    docker pull mysql:5.6.24
    echo "Downloading registry..."
    docker pull registry:2
    echo "Downloading services..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/apporbit-services
    docker tag ${INTERNAL_REGISTRY}/apporbit/apporbit-services apporbit/apporbit-services
    echo "Downloading controller..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/apporbit-controller
    docker tag ${INTERNAL_REGISTRY}/apporbit/apporbit-controller apporbit/apporbit-controller
    echo "Downloading RMQ..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/apporbit-rmq
    docker tag ${INTERNAL_REGISTRY}/apporbit/apporbit-rmq apporbit/apporbit-rmq
    echo "Downloading Docs..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/apporbit-docs
    docker tag ${INTERNAL_REGISTRY}/apporbit/apporbit-docs apporbit/apporbit-docs
    echo "Downloading CM..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/apporbit-chef:2.0
    docker tag ${INTERNAL_REGISTRY}/apporbit/apporbit-chef:2.0 apporbit/apporbit-chef:2.0
    echo "Downloading Consul..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/consul
    docker tag ${INTERNAL_REGISTRY}/apporbit/consul apporbit/apporbit-consul
    echo "Downloading Locator..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/locator
    docker tag ${INTERNAL_REGISTRY}/apporbit/locator apporbit/apporbit-locator
    echo "Downloading svcd..."
    docker pull ${INTERNAL_REGISTRY}/apporbit/svcd
    docker tag ${INTERNAL_REGISTRY}/apporbit/svcd apporbit/apporbit-svcd

    echo "Downloading infra containers..."

    for k in ${!infra_containers[@]}
    do
        docker pull gcr.io/google_containers/$k:${infra_containers[$k]}
        docker tag gcr.io/google_containers/$k:${infra_containers[$k]} google_containers/$k:${infra_containers[$k]}
    done

}

function save_images {

    mkdir -p appOrbitPackages
    cd appOrbitPackages
    echo "Saving image services..."
    docker save apporbit/apporbit-services > apporbit-services.tar
    echo "Saving image controller..."
    docker save apporbit/apporbit-controller > apporbit-controller.tar
    echo "Saving image RMQ..."
    docker save apporbit/apporbit-rmq > apporbit-rmq.tar
    echo "Saving image Docs..."
    docker save apporbit/apporbit-docs > apporbit-docs.tar
    echo "Saving image CM..."
    docker save apporbit/apporbit-chef:2.0 > apporbit-chef.tar
    echo "Saving image MySQL..."
    docker save mysql:5.6.24 > mysql.tar
    echo "Saving image Consul..."
    docker save apporbit/apporbit-consul > apporbit-consul.tar
    echo "Saving image Locator..."
    docker save apporbit/apporbit-locator > apporbit-locator.tar
    echo "Saving image svcd..."
    docker save apporbit/apporbit-svcd > apporbit-svcd.tar
    cd ..

    echo "Saving infra containers..."

    mkdir -p infra_images
    cd infra_images
    for k in ${!infra_containers[@]}
    do
        docker pull gcr.io/google_containers/$k:${infra_containers[$k]}
        docker save google_containers/$k:${infra_containers[$k]} > apporbit-$k.tar
    done
    cd ..

}

function generate_images_tar {
    tar -cvzf appOrbitPackages.tar.gz appOrbitPackages
}

function install_packaging_utils {
    echo "Installing yum-utils, createrepo"
    yum install -y yum-utils createrepo wget
}

function download_general_packages {
    echo "Downloading Nginx Passenger"
    CWD=`pwd`
    REPO="http://repos.gsintlab.com/release"
    mkdir -p appOrbitRPMs/noarch/
    cd appOrbitRPMs/noarch/
    wget -c ${REPO}/noarch/nginx-1.6.3.tar.gz
    wget -c ${REPO}/noarch/passenger-5.0.10.tar.gz
    cd "$CWD"

    echo "Downloading Passenger agent"
    mkdir -p appOrbitRPMs/noarch/5.0.7/
    cd appOrbitRPMs/noarch/5.0.7/
    wget -c ${REPO}/noarch/5.0.7/agent-x86_64-linux.tar.gz
    wget -c https://s3.amazonaws.com/phusion-passenger/binaries/passenger/by_release/5.0.7/nginx-1.6.3-x86_64-linux.tar.gz
    cd "$CWD"

    echo "Downloading mist jar"
    mkdir -p appOrbitRPMs/mist/master
    cd appOrbitRPMs/mist/master
    wget -c ${REPO}/mist/master/run.jar

    cd "$CWD"

}

function rhel_packages_setup {
    if [ "x$platform_id" == "xrhel" ]; then
        echo "Configuring RHEL repos for syncing..."
        sub_id=$(basename `ls /etc/pki/entitlement/*-key.pem | head -1` | cut -d'-' -f1)
        rhel_pkg_list=`cat rhel-pkglist.conf | xargs -I {} printf "{} "`

        cat <<EOF >> reposync.conf

[rhel-7-server-rpms]
name=Red Hat Enterprise Linux 7 Server (RPMs)
baseurl='https://cdn.redhat.com/content/dist/rhel/server/7/\$releasever/\$basearch/os'
sslverify=0
sslclientkey=/etc/pki/entitlement/${sub_id}-key.pem
sslclientcert=/etc/pki/entitlement/${sub_id}.pem
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
includepkgs=${rhel_pkg_list}
EOF
    fi
}

function generate_rpm_packages {
    echo "Generating rpm packages"
    mkdir -p appOrbitRPMs
    cd appOrbitRPMs
    cp ../reposync.conf .
    cp ../offline-pkglist.conf .
    cp ../updates-pkglist.conf .
    reposync -c reposync.conf
    wget -c https://opscode-omnibus-packages.s3.amazonaws.com/el/7/x86_64/chef-12.6.0-1.el7.x86_64.rpm
    rm -f reposync.conf offline-pkglist.conf updates-pkglist.conf
    createrepo .
    cd ..
    tar -cvzf appOrbitRPMs.tar.gz appOrbitRPMs
}


function build_offline_container {
    echo "Building apporbit offline container"
    cd Dockerfiles
    docker build -t apporbit/apporbit-offline -f offline-container .
    cd ..
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

function download_generate_gems {
    echo "Downloading ruby gems"
    mkdir -p appOrbitGems

    docker run -v $PWD/appOrbitGems:/opt/rubygems apporbit/apporbit-offline gem mirror
    echo "Generating ruby gems"
    tar -cvzf appOrbitGems.tar.gz appOrbitGems
}

function save_offline_container {
    docker save apporbit/apporbit-offline > apporbit-offline.tar
}

function save_registry_container {
    docker save registry:2 > registry.tar
}

function create_cargo_to_ship {
    tar -cvf appOrbitResources.tar apporbit-offline.tar registry.tar appOrbitRPMs.tar.gz appOrbitGems.tar.gz infra_images
    tar -cvf appOrbitPackages.tar appOrbitPackages

    echo "Dependent resources of appOrbit successfully downoaded and saved."

    echo "Transfer appOrbitResources.tar to a system that will act as resource provider for appOrbit Application."
    echo "Transfer appOrbitPackages.tar to a system where appOrbit Application will run."
}

function main {
    declare -rA infra_containers=(
        [dnsmasq]=1.1
        [kubedns-amd64]=1.5
        [exechealthz-amd64]=1.0
        [kubernetes-dashboard-amd64]=v1.1.0
        [pause-amd64]=3.0   
    )

    echo -n "Checking Internet Connectivity"
    check_internet
    echo "...[OK]"

    echo -n "Checking Platform Compatibility"
    check_platform
    echo "...[OK]"

    set_selinux

    get_internal_registry

    echo -n "Installing Docker"
    install_docker
    echo "...[OK]"

    echo -n "Downloading Images"
    download_images
    echo "...[OK]"

    echo -n "Saving Images"
    save_images
    echo "...[OK]"

    echo -n "Generating compressed tar of images"
    generate_images_tar
    echo "...[OK]"

    echo "Installing utils"
    install_packaging_utils
    echo "...[OK]"

    echo -n "Downloading compressed tar of RPMs"
    download_general_packages
    echo "...[OK]"

    rhel_packages_setup

    echo -n "Generating compressed tar of RPMs"
    generate_rpm_packages
    echo "...[OK]"

    echo -n "Building Offline Container Image"
    build_offline_container
    echo "...[OK]"

    echo -n "Generating compressed tar of ruby gems"
    download_generate_gems
    echo "...[OK]"

    echo -n "Saving Offline Container Image"
    save_offline_container
    echo "...[OK]"

    echo -n "Saving Registry Image"
    save_registry_container
    echo "...[OK]"

    echo -n "Generating archives to transfer"
    create_cargo_to_ship
    echo "...[OK]"
}

main
