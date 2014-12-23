#!/bin/bash
script_dir=`dirname "$0"`

cd $script_dir

echo 'Script started at ' `date` >> retweet.log

python retweet.py >> retweet.log 2>&1

echo 'Script ended at ' `date` >> retweet.log

