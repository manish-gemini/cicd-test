#!/bin/bash


#######################################################################################################
#      Script for pre-requisite all apporbit hosts
#######################################################################################################



LOG_FILE="/tmp/prereq_apporbit_host.log"

#Function to print log
# all logs will be redirect to log file
# log format eg : [process ID] [user] [date] [log message]
# [4201 :] [root][Fri Mar 3 05:44:18 EST 2017] - Configuring service
function printlog() {
    echo " [$$ :] [${USER}][`date`] - ${*}" >> ${LOG_FILE}
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


##### Execute Command over ssh and check exit status of command ############
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
    if [ $status -ne 0 ] || [ ${output[-1]} -ne 0 ]; then
        printlog "error while Executing Command $printCommand"
        exit $status
    fi
    ret_val=(${output[@]})
}


# Function which execute all commands reuired for apporbit host
function exec_commands() {
    # command to check line where kubelet service is going to start
    update_file="/opt/apporbit/chef/chef-repo/cookbooks/gemini_node/recipes/default.rb"
    cmd="docker exec -it apporbit-services bash -c \"grep -rn kubelet $update_file\" | awk -F : '{print \$1}'"
    execute_command_over_ssh $cmd
    output=(${ret_val[@]})
    if [[ -z ${output[0]} ]]
    then
        # Command to append lines in update file
        comm="\"execute \"mv /etc/resolv.conf /etc/resolv.conf.new\"\nexecute \"cp /etc/resolv.conf.bk /etc/resolv.conf\"\""
        cmd="docker exec -it apporbit-services bash -c \"echo -e  $comm | sudo tee -a $update_file\""
    else
        # Command to insert line before starting ‘kubelet’ service, 
        insert_line_no=$(( ${output[0]} -1))
        comm="\"sed -i '$insert_line_no"
        comm=$comm'i execute \"mv /etc/resolv.conf /etc/resolv.conf.new\" \nexecute \"cp /etc/resolv.conf.bk /etc/resolv.conf\"'
        cmd="docker exec -it apporbit-services bash -c $comm' $update_file\""
    fi  
    execute_command_over_ssh $cmd
    printlog "Done with updating file $update_file"
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


#Function to parse args
#extract key value from args eg: command params can be given in below format
#./Exec_prerequisite_on_apporbit_host.sh -user centos -ipaddress 104.197.143.211 -sshkey /root/esxi-vm.pem
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

