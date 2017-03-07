#!/bin/bash


#######################################################################################################
#      Script for pre-requisite on all google cloud nodes
#######################################################################################################



LOG_FILE="/tmp/prereq_gcp_vm.log"
ret_val=""

#Function to print log 
# all logs will be redirect to log file 
# log format eg : [process ID] [user] [date] [log message]
# [4201 :] [root][Fri Mar 3 05:44:18 EST 2017] - Configuring yum cron service...
function printlog() {
    echo " [$$ :] [${USER}][`date`] - ${*}" >> ${LOG_FILE}
}


#Function to executed commands over ssh
function execute_command_over_ssh() {
    local output=()
    command="$*"
    # create command to execute over ssh
    cmd="ssh -ttt -i $key -o StrictHostKeyChecking=no $user@$ipaddress sudo $command ; echo $?";
    printlog "Executing Command : $cmd"   
    output=( $($cmd 2>/dev/null ) )
    # execute command
    output=( $(echo ${output[@]} | sed -e 's/\r//g') )
    status=$?
    #check exit status of command
    if [ $status -ne 0 ] || [ ${output[-1]} -ne 0 ]; then
        printlog "error while Executing Command $printCommand"
        exit $status
    fi
    ret_val=(${output[@]})
}

#Function to enable root login over ssh      
function enable_root_over_ssh() {
    printlog "Enabling root login over SSH..."
    execute_command_over_ssh 'echo -e "PermitRootLogin yes"  | sudo tee -a /etc/ssh/sshd_config'
    execute_command_over_ssh "systemctl reload sshd" 
    execute_command_over_ssh "systemctl restart sshd"
    printlog "Enabling root login over ssh is  done"
   
}

#Function to set selinux permissive
function set_selinux_permissive() {
    printlog "Setting selinux permissive..."
    execute_command_over_ssh "setenforce 0"
    printlog "selinux set to permissive..."
}

#Function to take backup of old dns resolver file and create new one
function backup_and_update_dns_resolver() {
    printlog "Updating dns resolver config file..."
    execute_command_over_ssh "cp /etc/resolv.conf /etc/resolv.conf.bk"
    execute_command_over_ssh 'echo "nameserver 8.8.8.8" >>/etc/resolv.conf'
    printlog "Done with Updating dns resolver config file..."
} 

#Function to remove yum cron job packages
function configure_yum_cron_service() {
    printlog "Configuring yum cron service..."
    execute_command_over_ssh "rpm -e yum-cron"
    execute_command_over_ssh "mv /etc/yum/yum-cron.conf /etc/yum/yum-cron-hourly.conf"
    printlog "Configuring yum cron service successful..."
}

#Function to remove google packages 
function remove_google_packages() {
    printlog "Removing all google packages..."
    execute_command_over_ssh "yum erase -y google*"
    printlog "Done with erasing all google  packages"
}

#Function Stop google account daemon service, if it is running.
function stop_google_accounts_daemon() {
    printlog "Stoping google accounts daemon service..."
    execute_command_over_ssh "ps aux  |  grep -i google_accounts_daemon |  grep -v grep   | awk '{print \$2}' | xargs --no-run-if-empty sudo kill -9"
    printlog "Stoping google accounts daemon service...Done"
}

# Function to check if requiretty option is disable or not ###
function is_root_login_enable(){
    local output=()
    cmd="cat /etc/ssh/sshd_config |  grep -n \"PermitRootLogin yes\" | grep -v \"\#\" | sed 's/ \+/ /' | tail -1 | awk -F : '{print \$1}'"
    execute_command_over_ssh $cmd
    output=(${ret_val[@]})
    if [ ${#output[@]} -le 1 ]; then
        lastOccNo=1
    else 
        lastOccNo=${output[0]}
    fi
    cmd="tail -n +$lastOccNo /etc/ssh/sshd_config | grep -v \"\#\" | sed 's/ \+/ /' | grep  -n \"PermitRootLogin no\" | wc -l"
    execute_command_over_ssh $cmd
    output=(${ret_val[@]})
    if [ ${output[0]} -gt 0 ]; then
        printlog "root login over ssh is disable."
        return 1         
    fi
    return 0
}

#Function to execute all prereq on multiple hosts 
function execute_on_multi_host() {
    # read the file which contains multiple host  ssh login details
    array=( $(sed -n "/{/,/}/{s/[^:]*:[[:blank:]]*//p;}" $file ) )
    if [ $(( ${#array[@]}  % 3 )) -ne 0 ] ; then
        echo "Please enter all fields in file"
        exit 1   
    fi
    # get length of an array
    arraylength=${#array[@]}

    # use for loop to read all values and indexes
    for (( i=0; i<${arraylength}; i+=3 ));
    do 
        ipaddress=${array[$i]}
        user=${array[$i+1]}
        key=${array[$i+2], }
        # command to check the credentials of ssh login 
        ssh -q -o StrictHostKeyChecking=no -i $key $user@$ipaddress 'BatchMode=yes'
        status=$?
        if [ $status -ne 0 ]; then
            echo "SSH login failed. Please check credentials $ipaddress $user $key"
            exit $status
        else
            #If ssh login is successful then execute commands
            exec_commands
        fi
    done    
}

#Commands helper function
#Helper function will give information to the user how to pass params to script
usage()
{
    echo "usage: 
     PARAMETERS:
    -h <help> 
    -ipaddress <Static ipaddress> 
    -user <username>
    -sshkey  <ssh identity_file>
    -file <file with host details>"
}

#Function to parse args
#extract key value from args eg: command params can be given in below format
#./Exec_prerequisite_on_GCP_nodes.sh -user centos -ipaddress 104.197.143.211 -sshkey /root/esxi-vm.pem

function parse_args() {
    while [ "`echo $1 | cut -c1`" = "-" ]
    do
    case "$1" in

        -user)
               user=$2
               shift 2
            ;;
        -ipaddress)
               ipaddress=$2
                shift 2
            ;;

        -sshkey) 
                key=$2
                shift 2
            ;;
        
        -file) 
                file=$2
                shift 2
            ;;
        -h)
                usage
                exit 0 
            ;;
    esac
    done

}

#Function  to execute all pre_req commands
function exec_commands(){
    configure_yum_cron_service
    remove_google_packages
    stop_google_accounts_daemon
    backup_and_update_dns_resolver
    set_selinux_permissive
    is_root_login_enable
    if [ $? -eq 1 ];
        then 
        enable_root_over_ssh
    fi
}

### Entry point  Function ##########
function main(){
 
    parse_args  "$@" 
    if [  -z $1 ];
    then
        usage
        exit 1
    fi

    if [[ ! -z "$file" ]];
    then 
        execute_on_multi_host
    else
        exec_commands
    fi
    echo "All pre-requisites are executed successfully"    
    exit 0

}
main "$@"


