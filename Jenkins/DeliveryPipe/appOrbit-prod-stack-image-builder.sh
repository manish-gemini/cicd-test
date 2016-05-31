docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-services-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services-base apporbit/apporbit-services-base:latest


cp Dockerfiles/apporbitservices Dockerfile
cp apporbit-master.repo Dockerfiles/

cp /home/workspace/appOrbit-prod-mist-builder/label/ESXi-e2e-tester/run/generated/distributions/executable/run.jar  mist-cgp/

echo "[config]
SECRET_KEY=71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw=
INIT_VECTOR=f7BjRhMOAfuDNafQTSRJmg=" > apporbit.config.ini

#cp gemini.config.ini Dockerfiles/


echo "build:
  version:
    major: 1
    minor: 5
    patch: 00
    
  number: $TAG_NAME
  type: Master
  timestamp: `date +%s`" > build.yml
  

#cp /home/python_encryption.sh .
chmod 755 python_encryption.sh
./python_encryption.sh

tar cf apporbit-services.tar -T Dockerfiles/apporbitservices.lst
#cp -f apporbitservices.tar Dockerfiles/apporbitservices.tar
