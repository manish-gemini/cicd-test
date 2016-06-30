echo ${pwd}

ls

cd SPHINX/

rm -rf docs

git clone https://sajithgem:dogreat12@github.com/Gemini-sys/docs.git

cd docs

git checkout master

cd  ../docs/webdocs/

cp -rf * ../../IMAGE/source/

cd ../../

ls

sh Build-Docs.sh

echo "Build completed ...."

echo "pushing to staging registry"

docker tag -f apporbit/apporbit-docs jenkin-registry.gsintlab.com/apporbit/apporbit-docs

docker tag -f apporbit/apporbit-docs jenkin-registry.gsintlab.com/apporbit/apporbit-docs:$TAG_NAME

docker push jenkin-registry.gsintlab.com/apporbit/apporbit-docs
docker push jenkin-registry.gsintlab.com/apporbit/apporbit-docs:$TAG_NAME

