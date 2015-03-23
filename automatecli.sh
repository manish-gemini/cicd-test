echo "Starting Gemini Cli Build..."

echo "Enter the dir to checkout :"
read dirToCheckout
echo $dirToCheckout

if [ ! -d $dirToCheckout ]
then
	echo "Enter Valid Directory, exit.."
        exit
fi
cd $dirToCheckout
git clone https://sajithgem@github.com/Gemini-sys/Gemini-CLI.git

echo "SETUP Environment : 1 "
echo "Skip Settingup the Environment : 2 "
read setupEnv
echo $setupEnv

if [ $setupEnv -eq 1 ]
then
	echo "setting env variables"

	GOPATH=$dirToCheckout/Gemini-CLI
	PATH=$PATH:/usr/local/go/bin:$GOPATH/bin
	echo $GOPATH
	echo $PATH
fi
 echo $GOPATH
 echo $PATH


echo "GO TO CROSS COMIPLER..."
echo "Enter the dir to clone cross compiler"
read dirToCrossCompiler
echo $dirToCrossCompiler
echo "Printing GO To Cross Compiler...."
echo $GOPATH
echo $PATH
mkdir -p $dirToCrossCompiler
cd $dirToCrossCompiler
git clone git://github.com/davecheney/golang-crosscompile.git
echo "Printing GO To Cross Compiler...."
echo $GOPATH
echo $PATH

source golang-crosscompile/crosscompile.bash
go-crosscompile-build-all

cd $dirToCheckout/Gemini-CLI/src/github.com/gemini/

godep restore
go-linux-arm build
go-windows-amd64 build

