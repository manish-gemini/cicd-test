FROM centos:centos7.0.1406
MAINTAINER SPHINX doc builder  <sajith@gemini-systems.net> - sajith
RUN yum install -y epel-release
RUN yum install -y python python-pip make 

RUN /usr/bin/pip install sphinx sphinx-autobuild
ADD . /home/
WORKDIR /home/
ENTRYPOINT [ "/home/entrypoint.sh" ]
