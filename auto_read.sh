#!/bin/bash
cur_date=`date "+%Y-%m-%d-%H-%M"`

#ip=54.223.246.240
#expect_pid="0xB28EA0078258902D" #william

ip=47.115.122.110
#expect_pid="0x9EB8DB175E1521EC" #boat testing
#expect_pid="0xF7B6220C5054999B"
#expect_pid="0x9C76E0F7B1F9103C"
expect_pid="0x9F37E8B01B37F838"

#echo "scp tvu@192.168.1.190:/home/tvu/status_$ip status_$ip.xml"
#scp tvu@192.168.1.190:/home/tvu/status_$ip status_$ip.xml

begin_date=`grep '2020-' status_$ip.xml | head -1`
end_date=`grep '2020-' status_$ip.xml | tail -1`

echo "./readfile_server.py status_$ip.xml $expect_pid $begin_date $end_date > out_$ip"
#./readfile_server.py status_$ip.xml $expect_pid $begin_date $end_date > out_$ip
echo "./calltest.py status_$ip.xml $expect_pid $begin_date $end_date > out_$ip"
./calltest.py status_$ip.xml $expect_pid $begin_date $end_date > out_$ip
