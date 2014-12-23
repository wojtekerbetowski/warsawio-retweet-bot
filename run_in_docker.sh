#!/bin/bash
script_dir=`dirname "$0"`

cd $script_dir

docker build -t warsawio_retweet_bot . & docker run -v `pwd`:/source -it warsawio_retweet_bot

