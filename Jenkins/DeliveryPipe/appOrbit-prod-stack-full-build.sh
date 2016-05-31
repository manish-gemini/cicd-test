cd Dockerfiles
cp ../apporbit-master.repo apporbit.repo
cp ../CentOS-Base.repo .

docker build -t apporbit/apporbit-base -f apporbitBase .

docker login -u gemini -p dogreat12 https://jenkin-registry.gsintlab.com


docker tag -f apporbit/apporbit-base  jenkin-registry.gsintlab.com/apporbit/apporbit-base:$TAG_NAME
docker tag -f apporbit/apporbit-base  jenkin-registry.gsintlab.com/apporbit/apporbit-base

docker push jenkin-registry.gsintlab.com/apporbit/apporbit-base:$TAG_NAME
docker push jenkin-registry.gsintlab.com/apporbit/apporbit-base

cp apporbitservicesBase ../Dockerfile

###AFTER PUSH OF IMAGES 

docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services-base:$TAG_NAME apporbit/apporbit-services-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services-base:$TAG_NAME jenkin-registry.gsintlab.com/apporbit/apporbit-services-base
docker push jenkin-registry.gsintlab.com/apporbit/apporbit-services-base
