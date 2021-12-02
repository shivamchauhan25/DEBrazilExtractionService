#!/bin/bash

a=$1

st=$(echo "$a"|grep '/'|sed "/^$/d"|wc -l)

##echo $st

if [ "$st" == 1 ]
then
        dt=$(echo "$a" | awk -v FS=/ -v OFS=/ '{print $3,$2,$1}')
else
        dt=$(echo "$a" | awk -v FS=- -v OFS=- '{print $3,$2,$1}')
fi
echo "$dt"
