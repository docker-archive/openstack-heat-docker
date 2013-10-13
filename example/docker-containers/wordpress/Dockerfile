
FROM ubuntu:12.04
MAINTAINER Sam Alba <sam.alba@gmail.com>

# Install wordpress
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y install wordpress
RUN mv /var/www /var/www.old ; ln -sf /usr/share/wordpress /var/www

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2

ADD wp-config.php /etc/wordpress/wp-config.php
RUN chmod 655 /etc/wordpress/wp-config.php

EXPOSE 80

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
