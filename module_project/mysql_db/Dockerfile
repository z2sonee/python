FROM mysql:5.7

ADD ./init /docker-entrypoint-initdb.d
ADD ./init/init.sql /docker-entrypoint-initdb.d/
COPY ./init/utf8.cnf /etc/mysql/conf.d/

ENV MYSQL_ALLOW_EMPTY_PASSWORD true
ENV MYSQL_DATABASE phone_db
EXPOSE 3306

CMD ["mysqld"]
