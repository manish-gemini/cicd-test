echo %WORKSPACE%
set GOPATH=%WORKSPACE%\Gemini-CLI
set PATH=%PATH%;C:\Program Files\Git\cmd
set PATH=%PATH%;C:\Program Files (x86)\Bazaar
set PATH=%PATH%;C:\go\bin
set PATH=%PATH%;%GOPATH%\bin
rmdir %GOPATH% /s /q


git clone https://sajithgem:dogreat12@github.com/Gemini-sys/Gemini-CLI

cd Gemini-CLI


cd src\github.com\apporbit

go get github.com\tools\godep


godep go build --ldflags="-X main.Version 1.5.00.%TAG_NAME%"
godep go install --ldflags="-X main.Version 1.5.00.%TAG_NAME%"
