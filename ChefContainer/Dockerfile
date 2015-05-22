FROM centos:centos6.6
MAINTAINER  Gemini-CHEF <sajith@gemini-systems.net> -Sajith

RUN mkdir -p /opt/geminichef
ADD http://repos.gsintlab.com/repos/chef-server-11.1.6-1.el6.x86_64.rpm /opt/geminichef/
WORKDIR /opt/geminichef
RUN yum update -y; yum install -y chef-server-11.1.6-1.el6.x86_64.rpm; yum clean all
ADD . /opt/geminichef/
RUN chmod +x entrypoint.sh
EXPOSE 443
CMD ["bash", "-l", "-c", "/opt/geminichef/entrypoint.sh"]
