FROM centos:centos6.7
MAINTAINER  apporbit-CHEF <support@apporbit.com> -support

RUN mkdir -p /opt/apporbitchef /etc/init
WORKDIR /opt/apporbitchef
ADD pgdg-94-centos.repo /etc/yum.repos.d/
RUN yum install -y hostname postgresql94 postgresql94-server; yum update -y; yum localinstall -y http://repos.gsintlab.com/repos/x86_64/RPMS/chef-server-11.1.6-1.el6.x86_64.rpm; yum clean all
ADD chef-server.rb /etc/chef-server/chef-server.rb
ADD . /opt/apporbitchef/
RUN chmod +x entrypoint.sh
RUN \cp /usr/pgsql-9.4/bin/* /opt/chef-server/embedded/bin; \cp /usr/pgsql-9.4/lib/* /opt/chef-server/embedded/lib; \cp -rp /usr/pgsql-9.4/share/* /opt/chef-server/embedded/share
EXPOSE 9443
CMD ["bash", "-l", "-c", "/opt/apporbitchef/entrypoint.sh"]
