#/bin/bash
if [ ! -d /opt/intergation ]; then
    mkdir -p /opt/intergation
fi
cd /opt/intergation
rm -rf /opt/intergation/cicd
git clone https://prakash-gemini:l3tm3in@github.com/Gemini-sys/cicd.git
cd cicd
chmod 755 SourceEncoders/Encoder-automation.sh
sh SourceEncoders/Encoder-automation.sh
