
FROM ubuntu:12.04
MAINTAINER Sam Alba <sam.alba@gmail.com>

# Install mysql-server
RUN apt-get update
RUN apt-get -y install mysql-server pwgen
ADD start_mysqld.sh /start_mysqld.sh

# Bind on 0.0.0.0:3306
ADD mysqld-network.cnf /etc/mysql/conf.d/mysqld-network.cnf
EXPOSE 3306

ENTRYPOINT ["/start_mysqld.sh"]
