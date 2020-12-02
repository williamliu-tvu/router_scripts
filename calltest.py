#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import readfile_server as rdsvr
import sys
import datetime

def refine_begin_ts(ts):
    d1 = datetime.datetime.strptime(ts, '%Y-%m-%d-%H-%M-%S')
    day = d1.day
    if d1.hour > 16:
        day += 1
    str_d1 = "{:04d}-{:02d}-{:02d}-{:02d}-{:02d}".format(d1.year, d1.month, day, 16, 0)
    return str_d1

def refine_end_ts(ts):
    d1 = datetime.datetime.strptime(ts, '%Y-%m-%d-%H-%M-%S')
    day = d1.day
    if d1.hour < 16:
        day -= 1
    str_d1 = "{:04d}-{:02d}-{:02d}-{:02d}-{:02d}".format(d1.year, d1.month, day, 16, 0)
    return str_d1

if __name__ == "__main__":
    print("calltest.py ", sys.argv, file=sys.stderr)

    xml_filename = 'status_47.115.122.110.xml'
    ts_begin = '2020-05-26-06-00-00'
    ts_end = '2020-06-09-18-00-00'
    expect_pid = '0x9EB8DB175E1521EC'
    if len(sys.argv)==5:
        xml_filename = sys.argv[1]
        expect_pid = sys.argv[2]
        ts_begin = sys.argv[3]
        ts_end = sys.argv[4]
        
    #print('begin ', ts_begin, ' -> ', refine_begin_ts(ts_begin))
    #print('end   ', ts_end, ' -> ', refine_end_ts(ts_end))
    #d1 = datetime.datetime.strptime(refine_begin_ts(ts_begin), '%Y-%m-%d-%H-%M')
    #d2 = datetime.datetime.strptime(refine_end_ts(ts_end), '%Y-%m-%d-%H-%M')

    d1 = datetime.datetime.strptime(ts_begin, '%Y-%m-%d-%H-%M-%S')
    d2 = datetime.datetime.strptime(ts_end, '%Y-%m-%d-%H-%M-%S')

    new = d1
    for i in range ((d2-d1).days+1):
        nextday = new + datetime.timedelta(days=1)
        nextday_str = nextday.strftime("%Y-%m-%d-%H-%M")
        new_str = new.strftime("%Y-%m-%d-%H-%M")
        print(new_str, ' - ', nextday_str)
        new = new + datetime.timedelta(days=1)

        rdsvr.stat_xml(xml_filename, expect_pid, new_str, nextday_str)
