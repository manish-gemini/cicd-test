FROM centos:7.2.1511
MAINTAINER support@apporbit.com
# gcc for cgo
RUN yum install -y git curl wget hostname tar which zip bzip2 epel-release remi-release \
                 libffi-devel gcc gcc-c++ make pkg-config glibc-devel \
                 patch python python-devel kernel-devel automake && \
    yum -y update && yum install -y python-pip && yum -v clean expire-cache all

# Set Python Environment
ENV GOLANG_VERSION 1.6.3
ENV GOLANG_DOWNLOAD_URL https://golang.org/dl/go$GOLANG_VERSION.linux-amd64.tar.gz
ENV GOLANG_DOWNLOAD_SHA256 cdde5e08530c0579255d6153b08fdb3b8e47caabbe717bc7bcd7561275a87aeb

RUN curl -fsSL "$GOLANG_DOWNLOAD_URL" -o golang.tar.gz \
    && echo "$GOLANG_DOWNLOAD_SHA256  golang.tar.gz" | sha256sum -c - \
    && tar -C /usr/local -xzf golang.tar.gz \
    && rm golang.tar.gz

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"
WORKDIR $GOPATH

COPY go-wrapper /usr/local/bin/

# Set Python Environment
COPY requirements.txt /python/requirements.txt
RUN pip install -r /python/requirements.txt

ENV OUTPUTNAME apporbit
VOLUME /go/src/apporbit
VOLUME /go/bin
WORKDIR /go/src/apporbit
RUN pwd
COPY start /
CMD [ "bash",  "/start"  ]

