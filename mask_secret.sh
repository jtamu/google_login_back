#!/bin/bash

secret=$1

if [ -z $secret ]; then
    echo "\$secret is empty"
    exit 1
fi

masked="${secret:0:4}${secret//?/*}"
echo $masked
