#!/bin/bash -x
# installs to /opt/gradle
# existing versions are not overwritten/deleted
# seamless upgrades/downgrades
# $GRADLE_HOME points to latest *installed* (not released)
gradle_version=2.7
#mkdir /opt/gradle
wget -N http://services.gradle.org/distributions/gradle-${gradle_version}-all.zip
unzip ./gradle-${gradle_version}-all.zip -d /opt/
export PATH=$PATH:/opt/gradle-2.7/bin/

# check installation
gradle -v

