echo ${pwd}
cd ..
rm -rf cicd
git clone https://sajithgem:dogreat12@github.com/Gemini-sys/cicd.git
cd cicd
git checkout integration

echo ${pwd}

ls

cd SPHINX/

rm -rf docs

git clone https://sajithgem:dogreat12@github.com/Gemini-sys/docs.git

cd docs

git checkout integration

cd  ../docs/webdocs/

cp -rf * ../../IMAGE/source/

cd ../../

ls

sh Build-Docs.sh

echo "Build completed ...."

echo "pushing to staging registry"

docker login -u gemini -e admin@gemini-systems.net -p dogreat12 https://jenkin-registry.gsintlab.com

docker tag -f apporbit/apporbit-docs jenkin-registry.gsintlab.com/apporbit/apporbit-docs

#docker tag -f apporbit/apporbit-docs jenkin-registry.gsintlab.com/apporbit/jenkins-apporbit-docs:$TAG_NAME

docker push jenkin-registry.gsintlab.com/apporbit/apporbit-docs
#docker push jenkin-registry.gsintlab.com/apporbit/jenkins-apporbit-docs:$TAG_NAME

