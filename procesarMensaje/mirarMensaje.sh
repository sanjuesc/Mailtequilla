#!/bin/bash
while :
do
  echo "type 1" | mail > email.txt
  python3 mailToText.py
  sleep 5
done
