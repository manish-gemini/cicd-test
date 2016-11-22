if [ -f /go/bin/docker-compose ];
then
   echo "docker-compose already downloaded"
else
   curl -L https://github.com/docker/compose/releases/download/1.8.0/docker-compose-Linux-x86_64 > /go/bin/docker-compose
   chmod a+x /go/bin/docker-compose
fi

