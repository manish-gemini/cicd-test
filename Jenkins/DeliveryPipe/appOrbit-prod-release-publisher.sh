/bin/sh -x
docker pull secure-registry.gsintlab.com/apporbit/apporbit-docs
docker pull secure-registry.gsintlab.com/apporbit/apporbit-base
docker pull secure-registry.gsintlab.com/apporbit/apporbit-controller-base
docker pull secure-registry.gsintlab.com/apporbit/apporbit-services-base


docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-services:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-services:1.5-BUILD-$BUILD
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-services:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-services
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-controller

docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD registry.apporbit.com/apporbit/apporbit-docs

docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-controller-base registry.apporbit.com/apporbit/apporbit-controller-base
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-services-base registry.apporbit.com/apporbit/apporbit-services-base
docker tag -f secure-registry.gsintlab.com/apporbit/apporbit-base registry.apporbit.com/apporbit/apporbit-base

docker login -u apporbit03 -e admin@gemini-systems.net -p i27BMPr3gUsO https://registry.apporbit.com

docker push registry.apporbit.com/apporbit/apporbit-controller:1.5-BUILD-$BUILD
docker push registry.apporbit.com/apporbit/apporbit-services:1.5-BUILD-$BUILD
docker push registry.apporbit.com/apporbit/apporbit-docs:1.5-BUILD-$BUILD
docker push registry.apporbit.com/apporbit/apporbit-controller
docker push registry.apporbit.com/apporbit/apporbit-services
docker push registry.apporbit.com/apporbit/apporbit-docs


docker push registry.apporbit.com/apporbit/apporbit-controller-base
docker push registry.apporbit.com/apporbit/apporbit-services-base
docker push registry.apporbit.com/apporbit/apporbit-base

cp Customer/KIT/appOrbitDeploy/README.md Customer/KIT/appOrbitDeploy/src/.
cd Customer/KIT/appOrbitDeploy/src/
python -m compileall .
rm -f *.py
