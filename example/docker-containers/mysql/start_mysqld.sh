#!/bin/sh

ROOT_PWD=$(pwgen -s 12 1)

echo $ROOT_PWD
/usr/bin/mysqld_safe &
sleep 3
mysql 2>/dev/null <<EOF
UPDATE mysql.user SET Password=PASSWORD('$ROOT_PWD') WHERE User='root';
GRANT ALL ON *.* to root@'%' IDENTIFIED BY '$ROOT_PWD';
FLUSH PRIVILEGES;
CREATE DATABASE docker;
"
EOF
wait
