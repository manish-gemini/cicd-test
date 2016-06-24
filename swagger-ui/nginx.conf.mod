worker_processes      1;

events {
  worker_connections  1024;
}

http {
  include             mime.types;
  default_type        application/octet-stream;

  sendfile on;

  keepalive_timeout   65;

  #server {
  #  listen            8080;
  #  server_name       localhost;

   # location / {
   #   root            html;
   #   index           index.html index.htm;
   # }
  #}
  
     server{
          listen 80;
          server_name _;
          rewrite ^ https://$host$request_uri? permanent;
        }


    server {
        listen   443 default_server ssl;

        server_name _;
        root 		html;
	index		index.html index.htm;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	}

}
