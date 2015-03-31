#!/bin/bash
echo "Starting Gemini Cli Build..."

echo "Enter the dir to checkout :"
read dirToCheckout

if [ ! -d $dirToCheckout ]
then
	echo "Specified Directory does not exist., Creating the directory..."
	mkdir -p $dirToCheckout
fi

cd $dirToCheckout
echo "Git UserID: "
read gitID
git clone https://$gitID@github.com/Gemini-sys/Gemini-CLI.git

echo "setting env variables ..."
export GOPATH=$dirToCheckout/Gemini-CLI
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

echo "Enter the dir to clone cross compiler"
read dirToCrossCompiler

mkdir -p $dirToCrossCompiler
cd $dirToCrossCompiler
git clone git://github.com/davecheney/golang-crosscompile.git

source golang-crosscompile/crosscompile.bash
go-crosscompile-build-all
go get github.com/tools/godep

cd $dirToCheckout/Gemini-CLI/src/github.com/gemini/

godep restore
go-linux-amd64 build
go-windows-amd64 build

