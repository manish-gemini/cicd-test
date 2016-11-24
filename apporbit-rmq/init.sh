#!/bin/bash
declare -i wait_in_sec loop
wait_in_sec=2
loop=1
created=false

wait_for_host_port () {
  THOST=$1
  TPORT=$2
  declare -i foundHostPort
  foundHostPort=1
  while [ $foundHostPort -ne 0 ]; do
     echo "Waiting for host $THOST to respond at port $TPORT"
     loop=$(( loop + 1 ))
     sleep $(( wait_in_sec * loop ))
     timeout 1 bash -c "cat < /dev/null > /dev/tcp/$THOST/$TPORT"
     foundHostPort=$?
  done
  echo "Host: $THOST is responding at port $TPORT"
}

echo `date` "Starting apporbit-rmq container" 
# setup env vars
# Create Rabbitmq user
gosu root bash /docker-entrypoint.sh $@ &
 wait_for_host_port localhost 5672
 while [  "$created" == "false" ]; do
        rabbitmqctl list_users 2>/dev/null |grep -qs  "test"
        if [ $? -eq 0 ] ;
        then
            echo "*** User '$RABBITMQ_USER' with password '$RABBITMQ_PASSWORD' completed. ***" 
            created=true
            break
        else
            gosu root bash  /add-user.sh  
        fi
done
rabbitmqctl list_users
wait
