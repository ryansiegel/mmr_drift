#!/bin/bash

cd "$(dirname "$0")"

/usr/local/bin/python3.6 script/curl_leaderboards.py 
/usr/local/bin/python3.6 script/populate_readme.py 

git add *
git commit -m "$(date)"
git push

