FROM rabbitmq:3-management
# docker run -d --hostname my-rabbit --name some-rabbit -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management

# Define environment variables.
ENV RABBITMQ_VM_MEMORY_HIGH_WATERMARK_PAGING_RATIO=0.10
ENV RABBITMQ_USER test
ENV RABBITMQ_PASSWORD test
ADD init.sh /init.sh
ADD add-user.sh /add-user.sh

EXPOSE 15671 15672
EXPOSE 4369 5671 5672 25672

ENTRYPOINT ["/init.sh"]
CMD ["rabbitmq-server"]
