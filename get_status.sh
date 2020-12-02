#!/bin/bash

ip=$1
filename=status_$ip

while true
do
    echo `date "+%Y-%m-%d-%H-%M-%S"` >> $filename
    curl http://$ip:50500/status >> $filename
    sleep 10
done
