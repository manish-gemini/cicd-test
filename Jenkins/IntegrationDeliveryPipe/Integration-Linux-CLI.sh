export GOPATH=$WORKSPACE
export PATH=$PATH::/usr/local/go/bin:$GOPATH/bin

rm -rf $WORKSPACE/bin

cd $WORKSPACE/src/github.com/apporbit

/usr/local/go/bin/go get github.com/tools/godep


#/usr/local/go/bin/go get -u github.com/nicksnyder/go-i18n/goi18n
  #go get golang.org/x/crypto
#go get golang.org/x/crypto || true
#godep restore

#/usr/local/go/bin/go build -ldflags "-X main.Version 1.5.00.$TAG_NAME"
#/usr/local/go/bin/go install

#/usr/local/go/bin/go build --ldflags="-X main.Version 1.5.00.$TAG_NAME"
#/usr/local/go/bin/go install --ldflags="-X main.Version 1.5.00.$TAG_NAME"

#Mradul's feb1 changes
export GO15VENDOREXPERIMENT=0
godep go build --ldflags="-X main.Version 1.5.00.$TAG_NAME"
godep go install --ldflags="-X main.Version 1.5.00.$TAG_NAME"

#cd $WORKSPACE/

#cp /var/lib/jenkins/workspace/appOrbit-win-CLI/Gemini-CLI/bin/apporbit.exe $WORKSPACE/bin

cd $WORKSPACE/bin

cp -Rf $WORKSPACE/src/github.com/apporbit/samples .
cp -Rf $WORKSPACE/src/github.com/apporbit/i18n .
rm -rf i18n/i18n.go

zip -r apporbit-linux-cli.zip *
cp /var/lib/jenkins/workspace/Integration-win-CLI/Gemini-CLI/bin/apporbit.exe .

zip -r apporbit-windows-cli.zip apporbit.exe i18n samples

#zip -j apporbit-windows-cli.zip /var/lib/jenkins/workspace/appOrbit-win-CLI/Gemini-CLI/bin/apporbit.exe
