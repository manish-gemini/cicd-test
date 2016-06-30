docker login -u gemini -e admin@gemini-systems.net -p dogreat12 https://jenkin-registry.gsintlab.com

docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-docs:latest


docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller:$BUILD secure-registry.gsintlab.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services:$BUILD secure-registry.gsintlab.com/apporbit/apporbit-services:1.5-BUILD-$BUILD
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services:$BUILD secure-registry.gsintlab.com/apporbit/apporbit-services
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller:$BUILD secure-registry.gsintlab.com/apporbit/apporbit-controller
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-docs:latest secure-registry.gsintlab.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-docs:latest secure-registry.gsintlab.com/apporbit/apporbit-docs


docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base secure-registry.gsintlab.com/apporbit/apporbit-controller-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services-base secure-registry.gsintlab.com/apporbit/apporbit-services-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-base secure-registry.gsintlab.com/apporbit/apporbit-base

docker login -u admin -e admin@gemini-systems.net -p dogreat12 https://secure-registry.gsintlab.com

docker push secure-registry.gsintlab.com/apporbit/apporbit-services:1.5-BUILD-$BUILD
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD

sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-base
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-services-base
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-controller-base
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-services
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-controller
sleep 30
docker push secure-registry.gsintlab.com/apporbit/apporbit-docs






