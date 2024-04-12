FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY ./app/config/nginx/nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 443
