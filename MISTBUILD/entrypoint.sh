#!/bin/bash -x

#./gradleinstall.sh
export PATH=$PATH:/opt/gradle-2.7/bin/
git clone https://github.com/Gemini-sys/mist-cgp.git
cd mist-cgp
/opt/gradle-2.7/bin/gradle build run:export.run

