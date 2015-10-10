FROM centos:7
RUN yum install -y wget unzip java-1.8.0-openjdk git
ADD tools.jar /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.60-2.b27.el7_1.x86_64/jre/lib/
ADD entrypoint.sh /opt/
WORKDIR /opt/
RUN wget -N http://repos.gsintlab.com/repos/mist/gradle-2.7-all.zip; unzip ./gradle-2.7-all.zip -d /opt/;
ENTRYPOINT ["./entrypoint.sh"]

