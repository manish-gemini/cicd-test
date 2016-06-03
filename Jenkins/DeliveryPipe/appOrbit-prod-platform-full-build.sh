rm -rf apporbit-test.repo
rm -rf apporbit-release.repo
rm -rf apporbit-dev.repo

rm -f Gemfile-release

mv Gemfile-master Gemfile

cp Dockerfiles/apporbit-controller-base Dockerfile

docker login -u gemini -e admin@gemini-systems.net -p dogreat12 https://jenkin-registry.gsintlab.com
docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-base:$TAG_NAME
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-base:$TAG_NAME apporbit/apporbit-base

## AFTER BUILD AND PUBLISH USING DOCKER BUILD PLUGIN

docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base:$TAG_NAME apporbit/apporbit-controller-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base:$TAG_NAME jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base
docker push jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base
