#!/bin/bash
# Define variables
LSB=/usr/bin/lsb_release
 
 
# Purpose - Display header message
# $1 - message
function write_header(){
	local h="$@"
	echo "---------------------------------------------------------------" >> /var/log/apporbit/sysinfo.log
	echo "     ${h}" >> /var/log/apporbit/sysinfo.log
	echo "---------------------------------------------------------------" >> /var/log/apporbit/sysinfo.log
}
 
# Purpose - Get info about your operating system
function os_info(){
	write_header " System information "
	echo "Operating system : $(uname)" 
	[ -x $LSB ] && $LSB -a || echo "$LSB command is not insalled (set \$LSB variable)"
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
	ip -4 address show >> /var/log/apporbit/sysinfo.log
 
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
	vmstat >> /var/log/apporbit/sysinfo.log
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
echo "apporbit Sys logs ... "
echo "Log Location : /var/log/apporbit/sysinfo.log"
date > /var/log/apporbit/sysinfo.log

os_info >> /var/log/apporbit/sysinfo.log

cpu_info >> /var/log/apporbit/sysinfo.log

mem_info  >> /var/log/apporbit/sysinfo.log

hardDisk_info  >> /var/log/apporbit/sysinfo.log

host_info >> /var/log/apporbit/sysinfo.log

net_info >> /var/log/apporbit/sysinfo.log

user_info "who" >> /var/log/apporbit/sysinfo.log

user_info "last" >> /var/log/apporbit/sysinfo.log


write_header "Software Requirments "

docker_info >> /var/log/apporbit/sysinfo.log

selinux_info >> /var/log/apporbit/sysinfo.log

iptables_info >> /var/log/apporbit/sysinfo.log

dockerRun_info >> /var/log/apporbit/sysinfo.log

write_header "Read controller container log from /var/log/apporbit/controller.log"

docker logs apporbit-controller >>  /var/log/apporbit/controller.log

write_header "Read services container log from /var/log/apporbit/services.log"

docker logs apporbit-services >>  /var/log/apporbit/services.log

write_header "Read Mysql DB container log from /var/log/apporbit/db.log"

docker logs db >>  /var/log/apporbit/db.log

write_header "Read Chef container log from /var/log/apporbit/chef.log"

docker logs apporbit-chef >>  /var/log/apporbit/chef.log

docker exec -it apporbit-services bash -l -c "/home/apporbit/apporbit-services/utils/logmodule/master.sh"

echo "END OF apporbit SYS LOGS" >> /var/log/apporbit/sysinfo.log

 
