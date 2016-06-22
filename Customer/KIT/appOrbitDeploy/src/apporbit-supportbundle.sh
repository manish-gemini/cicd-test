#!/bin/bash
# Purpose - Display header message
# $1 - message
function write_header(){
	local h="$@"
	echo "---------------------------------------------------------------" >> /var/log/apporbit/host/sysinfo.log
	echo "     ${h}" >> /var/log/apporbit/host/sysinfo.log
	echo "---------------------------------------------------------------" >> /var/log/apporbit/host/sysinfo.log
}
 
# Purpose - Get info about your operating system
function os_info(){
	write_header " System information "
	echo "Operating system : "
	cat /etc/redhat-release
        cat /etc/centos-release
	write_header "Kernel Version "
	uname -a	
}
 
# Purpose - Get info about host such as dns, IP, and hostname
function host_info(){
	local dnsips=$(sed -e '/^$/d' /etc/resolv.conf | awk '{if (tolower($1)=="nameserver") print $2}')
	write_header " Hostname and DNS information "
	echo "Hostname : $(hostname -s)" 
	echo "DNS domain : $(hostname -d)"
	echo "Fully qualified domain name : $(hostname -f)" 
	echo "Network address (IP) :  $(hostname -i)"
	echo "DNS name servers (DNS IP) : ${dnsips}" 
}
 
# Purpose - Network inferface and routing info
function net_info(){
	devices=$(netstat -i | cut -d" " -f1 | egrep -v "^Kernel|Iface|lo")
	write_header " Network information "
	echo "Total network interfaces found : $(wc -w <<<${devices})" 
 
	echo "*** IP Addresses Information ***"
	ip -4 address show
 
	echo "***********************"
	echo "*** Network routing ***"
	echo "***********************" 
	netstat -nr
 
	echo "**************************************"
	echo "*** Interface traffic information ***" 
	echo "**************************************"
	netstat -i 
  
}
 
# Purpose - Display a list of users currently logged on 
#           display a list of receltly loggged in users   
function user_info(){
	local cmd="$1"
	case "$cmd" in 
		who) write_header " Who is online "; who -H ;;
		last) write_header " List of last logged in users "; last ;;
	esac 
}
 
# Purpose - Display used and free memory info
function mem_info(){
	write_header " Free and used memory "
	free -m 
 
    echo "*********************************" 
	echo "*** Virtual memory statistics ***"
    echo "*********************************"
	vmstat 2 5 >> /var/log/apporbit/host/sysinfo.log
    echo "***********************************" 
	echo "*** Top 5 memory eating process ***" 
    echo "***********************************"	
	ps auxf | sort -nr -k 4 | head -5
	
}

function hardDisk_info() {
	write_header "Free and Used Disk Space..."
	df -lh 
}

function cpu_info() {
	write_header "CPU Info..."
	cat /proc/cpuinfo
}

function docker_info() {
	write_header "Docker Info..."
	docker --version
	docker images
	docker ps -a

}

function selinux_info() {
	write_header "Selinux Info..."
	cat /etc/sysconfig/selinux 

}


function iptables_info() {
	write_header "IPTables Info..."
	iptables -L
}

function dockerRun_info() {
	write_header "Docker Run Info..."
	docker ps -a
}


#main logic
echo "appOrbit logs ... "
echo "Log Location : /var/log/apporbit/host/sysinfo.log"
mkdir -p /var/log/apporbit/host
date > /var/log/apporbit/host/sysinfo.log

os_info >> /var/log/apporbit/host/sysinfo.log

cpu_info >> /var/log/apporbit/host/sysinfo.log

mem_info  >> /var/log/apporbit/host/sysinfo.log

hardDisk_info  >> /var/log/apporbit/host/sysinfo.log

host_info >> /var/log/apporbit/host/sysinfo.log

net_info >> /var/log/apporbit/host/sysinfo.log

user_info "who" >> /var/log/apporbit/host/sysinfo.log

user_info "last" >> /var/log/apporbit/host/sysinfo.log


write_header "Software Requirments "

docker_info >> /var/log/apporbit/host/sysinfo.log

selinux_info >> /var/log/apporbit/host/sysinfo.log

iptables_info >> /var/log/apporbit/host/sysinfo.log

dockerRun_info >> /var/log/apporbit/host/sysinfo.log

write_header "Read Platform container log from /var/log/apporbit/host/platform.log"

docker logs apporbit-controller >>  /var/log/apporbit/host/platform.log

write_header "Read Stack container log from /var/log/apporbit/host/stack.log"

docker logs apporbit-services >>  /var/log/apporbit/host/stack.log

write_header "Read Mysql DB container log from /var/log/apporbit/host/db.log"

docker logs apporbit-db >>  /var/log/apporbit/host/db.log

write_header "Read Chef container log from /var/log/apporbit/host/chef.log"

docker logs apporbit-chef >>  /var/log/apporbit/host/chef.log

docker exec -it apporbit-services bash -l -c "/home/apporbit/apporbit-services/utils/logmodule/master.sh"

echo "END OF APPORBTI SYS LOGS" >> /var/log/apporbit/host/sysinfo.log

mkdir -p /opt
NOW=$(date +"%H-%M-%m-%d-%Y")
echo "Find LOG Bundle at /opt/var_log_apporbit$NOW.tar.gz"
tar -cvzf /opt/var_log_apporbit$NOW.tar.gz /var/log/apporbit > /dev/Null
 
