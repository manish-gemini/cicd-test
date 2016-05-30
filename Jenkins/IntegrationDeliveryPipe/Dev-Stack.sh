echo "[config]
SECRET_KEY=71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw=
INIT_VECTOR=f7BjRhMOAfuDNafQTSRJmg=" > apporbit.config.ini

cp mist-cgp/label\=integration.gsintlab.com/run.jar mist-cgp/

docker login -u gemini -e admin@gemini-systems.net -p dogreat12 https://jenkin-registry.gsintlab.com

docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-base
docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-services-base

docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-base apporbit/apporbit-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-services-base apporbit/apporbit-services-base



BuildNumber=`expr $BUILD_NUMBER + 1000`

echo "build:
  version:
    major: 1
    minor: 0
    patch: 00
    
  number: $BuildNumber
  type: Integration
  timestamp: `date +%s`" > build.yml
  
  
#cp /home/python_encryption.sh .

chmod 755 python_encryption.sh

./python_encryption.sh

#cd Dockerfiles
#cp ../gemini.repo .
#cp ../CentOS-Base.repo .

#docker build -t gemini/gemini-base -f GeminiBase .
#docker build -t gemini/gemini-stack-base -f GeminiStackBase .

#cd ..
#echo "Build Tar file for GeminiStack ..."
cp apporbit.config.ini Dockerfiles/
tar cf Dockerfiles/apporbit-services.tar -T Dockerfiles/apporbitservices.lst


#cd Dockerfiles

#Temporary fix for repos selection

echo > Dockerfiles/apporbitservicesTestrepo

sed '1 a ADD apporbit-test.repo /etc/yum.repos.d/' Dockerfiles/apporbitservices  >> Dockerfiles/apporbitservicesTestrepo

cp Dockerfiles/apporbitservicesTestrepo Dockerfile
cp Dockerfiles/apporbit-services.tar apporbit-services.tar




echo "Build Stack Image..."

#docker build -t gemini/gemini-stack -f GeminiStack .
#rm GeminiStack.tar gemini.config.ini gemini.repo



#docker tag -f gemini/gemini-stack  integration.gsintlab.com/gemini/gemini-stack-trigger
