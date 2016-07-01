FROM alpine:3.3

MAINTAINER Roman Tarnavski

RUN apk add --update nginx
COPY apporbitserver.key /
COPY apporbitserver.crt /
COPY nginx.conf /etc/nginx/
ADD ./dist/ /usr/share/nginx/html
# replace index.html
ADD index.html /usr/share/nginx/html/
ADD swagger.html /usr/share/nginx/html/

# create www folders and expose
RUN mkdir -p /var/www/apporbit
RUN ln -s /usr/share/nginx/html/api-docs /var/www/apporbit

EXPOSE 443 8080

CMD nginx -g 'daemon off;'
