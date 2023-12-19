FROM nginx:alpine

# Заменяем дефолтную страницу nginx соответствующей веб-приложению
#RUN rm -rf /usr/share/nginx/html/*
COPY ./nginx_from_image.conf /etc/nginx/nginx.conf

#RUN rm /etc/nginx/conf.d/default.conf
#COPY ./nginx_from_image.conf /etc/nginx/conf.d/

ENTRYPOINT ["nginx", "-g", "daemon off;"]