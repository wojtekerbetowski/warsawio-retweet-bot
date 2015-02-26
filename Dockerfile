FROM python:2-onbuild

ADD retweet.py /source/retweet.py

CMD while true; do python retweet.py; sleep 300; done

