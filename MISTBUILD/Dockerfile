FROM centos:7
RUN yum install -y wget unzip java-1.8.0-openjdk
#RUN mkdir '/opt/gradle'
#RUN wget -N https://services.gradle.org/distributions/gradle-2.7-all.zip
ADD gradleinstall.sh /opt/
ADD tools.jar /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.60-2.b27.el7_1.x86_64/jre/lib/
WORKDIR /opt
CMD[./gradleinstall.sh]

