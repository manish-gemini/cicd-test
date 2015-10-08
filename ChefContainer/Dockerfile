FROM centos:centos6.7
#FROM centos:centos7.1.1503
MAINTAINER  Gemini-CHEF <sajith@gemini-systems.net> -Sajith

RUN mkdir -p /opt/geminichef /etc/init
WORKDIR /opt/geminichef
ADD pgdg-94-centos.repo /etc/yum.repos.d/
RUN yum install -y hostname postgresql94 postgresql94-server; yum update -y; yum localinstall -y http://repos.gsintlab.com/repos/x86_64/RPMS/chef-server-11.1.6-1.el6.x86_64.rpm; yum clean all
#RUN yum install -y hostname postgresql94 postgresql94-server; yum update -y; yum localinstall -y https://web-dl.packagecloud.io/chef/stable/packages/el/7/chef-server-core-12.2.0-1.el7.x86_64.rpm; yum clean all
ADD chef-server.rb /etc/chef-server/chef-server.rb
ADD . /opt/geminichef/
RUN chmod +x entrypoint.sh
RUN mkdir -p /etc/init
RUN \cp /usr/pgsql-9.4/bin/* /opt/chef-server/embedded/bin; \cp /usr/pgsql-9.4/lib/* /opt/chef-server/embedded/lib; \cp -rp /usr/pgsql-9.4/share/* /opt/chef-server/embedded/share
EXPOSE 9443
CMD ["bash", "-l", "-c", "/opt/geminichef/entrypoint.sh"]
