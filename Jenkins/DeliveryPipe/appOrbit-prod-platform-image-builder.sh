#Ruby encoding.

cp /home/ruby_encryption.sh .

./ruby_encryption.sh

#cp /home/libtest.sh .

rm -rf config/routes/v1.rb
rm -rf config/routes/v2.rb
mv config/routes/v1.rb.bak config/routes/v1.rb
mv config/routes/v2.rb.bak config/routes/v2.rb


find . -type f -name "*.rb.bak"  -exec rm -f {} \;



#docker login -u admin -e admin@gemini-systems.net -p $Dogreat12 https://jenkin-registry.gsintlab.com


#Build number

cd config
echo "build:
  version:
    major: 1
    minor: 5
    patch: 00
    
  number: $TAG_NAME
  type: Master
  timestamp: `date +%s`" > build.yml
  
cd ..

docker pull jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base
docker tag -f jenkin-registry.gsintlab.com/apporbit/apporbit-controller-base apporbit/apporbit-controller-base:latest
  
cp Dockerfiles/apporbit-controller Dockerfile
