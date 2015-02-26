FROM python:2-onbuild

WORKDIR /source

CMD while true; do python retweet.py; sleep 300; done

