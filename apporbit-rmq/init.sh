#!/bin/bash
declare -i wait_in_sec loop
wait_in_sec=2
loop=1
created=false
# Create Rabbitmq user
gosu root bash /docker-entrypoint.sh $@ &
 sleep 10
 while [  "$created" == "false" ]; do
    pgrep beam.smp >/dev/null 2>&1
    if [ $? -eq 0 ] ;
    then 
        rabbitmqctl list_users 2>/dev/null |grep -qs  "test"
        if [ $? -eq 0 ] ;
        then
            echo "*** User '$RABBITMQ_USER' with password '$RABBITMQ_PASSWORD' completed. ***" 
            created=true
            break
        else
            gosu root bash  /add-user.sh & 
            loop=$(( loop + 1 ))
            sleep $(( wait_in_sec * loop ))
        fi
    else
        echo "Waiting to add User '$RABBITMQ_USER' " sleep  loop
        loop=$(( loop + 1 ))
        sleep $(( wait_in_sec * loop ))
    fi
done
rabbitmqctl list_users
wait
