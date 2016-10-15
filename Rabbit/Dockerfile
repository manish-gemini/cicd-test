FROM rabbitmq:3-management
# docker run -d --hostname my-rabbit --name some-rabbit -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
# Define environment variables.
ENV RABBITMQ_DEFAULT_USER test
ENV RABBITMQ_DEFAULT_PASSWORD test

#ADD init.sh /init.sh
EXPOSE 15671 15672
EXPOSE 4369 5671 5672 25672
# Define default command
#CMD ["/init.sh"]
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["rabbitmq-server"]
