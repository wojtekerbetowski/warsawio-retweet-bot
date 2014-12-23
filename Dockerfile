FROM python:2-onbuild

WORKDIR /source

RUN apt-get update
RUN apt-get -y install cron
RUN apt-get -y install rsyslog

RUN echo '*/5 * * * * /usr/local/bin/python /source/retweet.py >> /source/retweet.log 2>&1\n' > /var/spool/cron/crontabs/root

RUN chmod -R 0600 /var/spool/cron/crontabs/

RUN touch /var/log/syslog
RUN touch /source/retweet.log

CMD rsyslogd && cron && tail -f /var/log/syslog /var/log/cron.log /source/retweet.log

