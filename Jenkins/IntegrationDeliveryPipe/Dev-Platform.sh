docker login -u gemini -e admin@gemini-systems.net -p dogreat12 https://jenkin-registry.gsintlab.com

docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-base
docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base

docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-base apporbit/apporbit-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base  apporbit/apporbit-controller-base

#Ruby encoding.

#/var/lib/jenkins/ruby_encryption.sh


#Build number

BuildNumber=`expr $TAG_NAME + 1000`


cd config
echo "build:
  version:
    major: 1
    minor: 5
    patch: 00
    
  number: $BuildNumber
  type: Integration
  timestamp: `date +%s`" > build.yml
  
cd ..


#changes
#cd Dockerfiles
#cp ../gemini.repo .

#docker build -t gemini/gemini-base -f GeminiBase .

#echo "Gemini Platform Base Image..."
#cp ../Gemfile .
#docker build -t gemini/gemini-platform-base -f GeminiPlatformBase .
#rm Gemfile gemini.repo 
#cd ..

echo "Gemini Platform Image..."
#docker build -t jenkin-registry.gsintlab.com/gemini/gemini-platform-trigger -f Dockerfiles/GeminiPlatform .
cp Dockerfiles/apporbit-controller Dockerfile

#docker tag -f gemini/gemini-platform  integration.gsintlab.com/gemini/gemini-platform-trigger
#docker push jenkin-registry.gsintlab.com/gemini/gemini-platform-trigger
