FROM centos:centos7.0.1406
MAINTAINER SPHINX doc builder  <sajith@apporbit.io> - sajith
RUN yum install -y epel-release

RUN yum install -y python python-pip make nginx 

RUN /usr/bin/pip install sphinx sphinx-autobuild recommonmark sphinx_rtd_theme

ADD source /home/source
ADD *.html /home/source/
ADD nginx.conf /etc/nginx/
#ADD entrypoint.sh /home/source/

WORKDIR /home/source

RUN cd /home/source && sphinx-build -b html . _build/html


EXPOSE 80

CMD ["bash", "-l", "-c", "/usr/sbin/nginx -g \"daemon off;\""]

