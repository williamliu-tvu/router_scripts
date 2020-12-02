#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
#import matplotlib.pyplot as plt
import time
import matplotlib.pyplot as plt

import json
import xmltodict

import datetime

import numpy as np

def diff_date(ts1,ts2):
    d1=datetime.datetime.strptime(ts1, '%Y-%m-%d-%H-%M-%S')
    d2=datetime.datetime.strptime(ts2, '%Y-%m-%d-%H-%M-%S')
    return d2-d1

class StatRouter:
    # https://www.cnblogs.com/wenqiangit/p/11277254.html
    def __init__(self):
        self.break_ts=[]
        self.break_type=[]

    def update(self, timestamp, break_type):
        ts=datetime.datetime.strptime(timestamp, '%Y-%m-%d-%H-%M-%S')
        self.break_ts.append(ts)
        self.break_type.append(break_type)

    def output_break_type(self, break_type):
        if (break_type==1): 
            return "only root node"
        elif (break_type==2):
            return "connected==no"
        elif (break_type==3):
            return "duration<last_duration"
        elif (break_type==4):
            return "pid not found"
        elif (break_type==0):
            return "begin"
        elif (break_type==9):
            return "end"
        else:
            return "unknown"

    def output(self):
        print('Router line broken statistics:')
        for i in range(len(self.break_ts)):
            if i!=0:
                delta = self.break_ts[i] - self.break_ts[i-1]
                print(self.break_ts[i-1], ' - ', self.break_ts[i], delta, self.output_break_type(self.break_type[i-1]), ",", self.output_break_type(self.break_type[i]))
        print('')

        begin=self.break_ts[0]
        begin_type=self.break_type[0]
        if len(self.break_ts)>1:
            end=self.break_ts[1]
            end_type=self.break_type[1]
        break_duration=datetime.timedelta(seconds=0)
        for i in range(len(self.break_ts)):
            if i!= 0:
                delta = self.break_ts[i] - self.break_ts[i-1]
                if delta>datetime.timedelta(seconds=11):
                    if i>0:
                        if break_duration!=datetime.timedelta(seconds=0):
                            print(begin, ' - ', self.break_ts[i-1], break_duration, self.output_break_type(begin_type), self.output_break_type(self.break_type[i-1]))
                        else:
                            if i>1:
                                print(begin, ' - ', self.break_ts[i-1], 'less than 10 seconds', self.output_break_type(begin_type), self.output_break_type(self.break_type[i-1]))
                        begin=self.break_ts[i-1]
                        begin_type=self.break_type[i-1]
                        print(begin, ' - ', end, (end-begin), self.output_break_type(begin_type), self.output_break_type(end_type))
                    else:
                        print(begin, ' - ', end, (end-begin), self.output_break_type(begin_type), self.output_break_type(end_type))
                    begin=self.break_ts[i]
                    begin_type=self.break_type[i]
                    break_duration=datetime.timedelta(seconds=0)
                else:
                    break_duration+=delta

                if i<(len(self.break_ts)-1):
                    end=self.break_ts[i+1]
                    end_type=self.break_type[i+1]

class Stat:
    def __init__(self):
        self.total_recv_bytes=0 #final data of every broken session
        self.total_send_bytes=0
        self.init_recv_bytes=0 #begin data of every broken session
        self.init_send_bytes=0
        self.inc_recv_bytes=0
        self.inc_send_bytes=0
        self.last_recv_bytes=0
        self.last_send_bytes=0
        self.break_timestamp=[]
        self.break_ip=[]
        self.last_timestamp=''
        self.last_ip=''
        if hasattr(self, 'begin_ts')==False:
            self.begin_ts=''

        self.rtt=[]

        if hasattr(self, 'first_total_recv_bytes')==False:
            self.first_total_recv_bytes=0 # begin data of time set
            self.final_total_recv_bytes=0 # final data of time set
        if hasattr(self, 'first_total_send_bytes')==False:
            self.first_total_send_bytes=0
            self.final_total_send_bytes=0

    def set_begin_ts(self, new_begin_ts):
        self.begin_ts = new_begin_ts

    def update(self, timestamp, ip, recv_bytes, send_bytes):
        #if ip!=self.last_ip:
        if int(recv_bytes)<self.last_recv_bytes:
            #print("ip!=self.last_ip", timestamp, ip)
            print("recv_bytes < last_recv_bytes", timestamp, ip, self.last_ip, recv_bytes, self.last_recv_bytes, send_bytes, self.last_send_bytes)
            self.break_ip.append(ip)
            self.break_timestamp.append(timestamp)
            self.inc_recv_bytes=int(recv_bytes)
            self.inc_send_bytes=int(send_bytes)
        else:
            self.inc_recv_bytes=int(recv_bytes)-self.last_recv_bytes
            self.inc_send_bytes=int(send_bytes)-self.last_send_bytes

        if self.first_total_recv_bytes==0:
            self.first_total_recv_bytes=self.inc_recv_bytes
            self.init_recv_bytes=self.inc_recv_bytes
            #print('self.first_total_recv_bytes=self.inc_recv_bytes', self.inc_recv_bytes)
        if self.first_total_send_bytes==0:
            self.first_total_send_bytes=self.inc_send_bytes
            self.init_send_bytes=self.inc_send_bytes
            #print('self.first_total_send_bytes=self.inc_send_bytes', self.inc_send_bytes)

        self.final_total_recv_bytes+=self.inc_recv_bytes
        self.final_total_send_bytes+=self.inc_send_bytes

        self.total_recv_bytes+=self.inc_recv_bytes
        self.total_send_bytes+=self.inc_send_bytes
        self.last_recv_bytes=int(recv_bytes)
        self.last_send_bytes=int(send_bytes)
        self.last_ip=ip
        self.last_timestamp=timestamp

    def output(self, head):
        print(head, "recv_bytes {:.3f} Mbytes send_bytes {:.3f} Mbytes".format(self.total_recv_bytes/1024.0/1024.0, self.total_send_bytes/1024.0/1024.0))

    def output_delta(self, head):
        delta_recv_bytes = self.total_recv_bytes - self.init_recv_bytes
        delta_send_bytes = self.total_send_bytes - self.init_send_bytes
        print(head, "recv_bytes {:.3f} Mbytes send_bytes {:.3f} Mbytes".format(delta_recv_bytes/1024.0/1024.0, delta_send_bytes/1024.0/1024.0))

    def output_alldelta(self, head):
        delta_recv_bytes = self.final_total_recv_bytes - self.first_total_recv_bytes
        delta_send_bytes = self.final_total_send_bytes - self.first_total_send_bytes
        print(head, "recv_bytes {:.3f} Mbytes send_bytes {:.3f} Mbytes".format(delta_recv_bytes/1024.0/1024.0, delta_send_bytes/1024.0/1024.0))
        print(head, "recv_bytes {:.3f} Mbytes send_bytes {:.3f} Mbytes".format(delta_recv_bytes/1024.0/1024.0, delta_send_bytes/1024.0/1024.0), file=sys.stderr)

    def output_broken(self, head):
        global current_ts
        print(head, "line broken total (the timestamp when recv_bytes < last_recv_bytes)", len(self.break_timestamp), len(self.break_ip))
        print('begin_ts ', self.begin_ts)
        delta = 0
        for i in range(len(self.break_timestamp)):
            if i>=1:
                delta = diff_date(self.break_timestamp[i-1], self.break_timestamp[i])
                print(i, self.break_timestamp[i], self.break_ip[i], delta)
            else:
                delta = diff_date(self.begin_ts, self.break_timestamp[i])
                print('~', self.break_timestamp[i], self.break_ip[i], delta)
        break_ts_len = len(self.break_timestamp)
        if (break_ts_len>0):
            delta = diff_date(self.break_timestamp[break_ts_len-1], current_ts)
            print(self.break_timestamp[break_ts_len-1], '~', self.break_ip[break_ts_len-1], delta)
        print("")

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    time_stamp = "%s" % (data_head)
    return time_stamp

def get_status(timestamp, content, count, expect_pid):
    global ts
    global st,st1,st2,st3,st4, last_duration,last_router_ip
    global t, rtt_list1, rtt_list2, rtt_list3, rtt_list4
    global recv_bytes_list, recv_bytes_list1, recv_bytes_list2, recv_bytes_list3, recv_bytes_list4
    global send_bytrs_list, send_bytes_list1, send_bytes_list2, send_bytes_list3, send_bytes_list4
    global router_reset
    global stRouter

    rtt1=0
    rtt2=0
    rtt3=0
    rtt4=0

    recv_bytes1=0
    recv_bytes2=0
    recv_bytes3=0
    recv_bytes4=0
    send_bytes1=0
    send_bytes2=0
    send_bytes3=0
    send_bytes4=0

    xml_dict=xmltodict.parse(content)
    json_str = json.dumps(xml_dict, indent=1)

    ts.append(timestamp)
    t.append(count)
    if len(xml_dict["root"])<=3:
        rtt_list1.append(int(rtt1))
        rtt_list2.append(int(rtt2))
        rtt_list3.append(int(rtt3))
        rtt_list4.append(int(rtt4))

        recv_bytes_list.append(int(0))
        send_bytes_list.append(int(0))

        recv_bytes_list1.append(int(recv_bytes1))
        recv_bytes_list2.append(int(recv_bytes2))
        recv_bytes_list3.append(int(recv_bytes3))
        recv_bytes_list4.append(int(recv_bytes4))
        send_bytes_list1.append(int(send_bytes1))
        send_bytes_list2.append(int(send_bytes2))
        send_bytes_list3.append(int(send_bytes3))
        send_bytes_list4.append(int(send_bytes4))

        st_output_all()
        st_output_delta_all()
        #st_output_alldelta_all()
        st_output_broken_all()
        st_init_all()
        print(timestamp, 'stat reset type1 only root node')
        stRouter.update(timestamp, 1)
        print('')
        return

    status=xml_dict["root"]["status"]
    svr_connected = status['@connected']
    svr_router_num = int(status['@connectedPeersNum'])

    stat=xml_dict["root"]["statistics"]

    if svr_router_num !=0:
        svr_router_list = status['connectedPeers']['connectedPeer']
        svr_duration = float(stat['@runningTimeInSeconds'])/3600.0/24.0
        svr_recv_bytes = float(stat['@receivedBytesSinceStart'])/1024.0/1024.0/1024.0
        svr_send_byres = float(stat['@sentBytesSinceStart'])/1024.0/1024.0/1024.0
        svr_recv_bps = float(stat['@receivedBitsPerSecond'])/1024.0/1024.0
        svr_send_bps = float(stat['@sentBitsPerSecond'])/1024.0/1024.0
        print(svr_router_num, 'routers {:.2f} days {:.2f} GBytes {:.2f} GBytes {:.2f} Mbps {:.2f} Mbps'.format(svr_duration, svr_recv_bytes, svr_send_byres, svr_recv_bps, svr_send_bps), end=' ')

        if type(svr_router_list).__name__ == 'list':
            svr_router_len = len(svr_router_list)
            for i in range(svr_router_len):
                print(svr_router_list[i]['@peerId'], end=' ')
            print('')
        elif type(svr_router_list).__name__ == 'OrderedDict':
            svr_router_len = 1
            print(svr_router_list['@peerId'])

    peer=xml_dict["root"]["peers"]["peer"]

    #<class 'collections.OrderedDict'>, this is only one peer
    #<class 'list'>
    if type(peer).__name__=='OrderedDict':
        pid=peer["@peerId"]
        n=1
    elif type(peer).__name__=='list':
        n=len(xml_dict["root"]["peers"]["peer"])
    else:
        print("new type", type(peer).__name__)

    found=0
    for i in range(n):
        if n==1:
            pid=peer["@peerId"]
            x=peer
        else:
            pid=peer[i]["@peerId"]
            x=peer[i]

        if pid==expect_pid:
            found=1
        else:
            continue

        connected=x["@connected"]
        if connected=='no':
            print(pid, connected)
            st_output_all()
            st_output_delta_all()
            #st_output_alldelta_all()
            st_output_broken_all()
            st_init_all()
            print(timestamp, 'stat reset type2 found pid but connected==no')
            stRouter.update(timestamp, 2)

        if connected=='yes':
            duration=x["@connectedTimeInSeconds"]
            recv_total_bps=x["@receivedBitsPerSecond"]
            send_total_bps=x["@sentBitsPerSecond"]
            recv_total_bytes=x["@receivedBytesInSession"]
            send_total_bytes=x["@sentBytesInSession"]
            print(pid, connected, duration, "s", "recv_bytes", recv_total_bytes, "send_bytes", send_total_bytes, "recv_bps", recv_total_bps, "send_bps", send_total_bps)
            if int(duration)<int(last_duration):
                st_output_all()
                st_output_delta_all()
                #st_output_alldelta_all()
                st_output_broken_all()
                st_init_all()
                print(timestamp, 'stat reset type3 duration<last_duration(bytes should also <)', duration, last_duration)
                stRouter.update(timestamp, 3)

            st.update(timestamp, '0', recv_total_bytes, send_total_bytes)
            last_duration=duration
            recv_bytes_list.append(int(recv_total_bytes))
            send_bytes_list.append(int(send_total_bytes))

            conn=x["connections"]["connection"]
            if type(conn).__name__=='OrderedDict':
                m=1
            elif type(conn).__name__=='list':
                m=len(conn)
            else:
                print("new type", type(conn).__name__)
            for j in range(m):
                if m==1:
                    c=x["connections"]["connection"]
                else:
                    c=x["connections"]["connection"][j]
                ip=c["@remoteAddress"]
                connected=c["@connected"]
                slot=c["@localSlotId"]
                rslot=c["@remoteSlotId"]
                recv_bps=c["@receivedBitsPerSecond"]
                send_bps=c["@sentBitsPerSecond"]
                recv_bytes=c["@receivedBytesInSession"]
                send_bytes=c["@sentBytesInSession"]
                rtt=c["@rttInMsec"]
                print("slot", rslot, connected, ip, "rtt", rtt, "recv_bytes", recv_bytes, "send_bytes", send_bytes, "recv_bps", recv_bps, "send_bps", send_bps)
                if rslot=="1":
                    if connected=='yes':
                        st1.update(timestamp, ip, recv_bytes, send_bytes)
                    rtt1=rtt
                    recv_bytes1=recv_bytes
                    send_bytes1=send_bytes
                if rslot=="2":
                    if connected=='yes':
                        st2.update(timestamp, ip, recv_bytes, send_bytes)
                    rtt2=rtt
                    recv_bytes2=recv_bytes
                    send_bytes2=send_bytes
                if rslot=="3":
                    if connected=='yes':
                        st3.update(timestamp, ip, recv_bytes, send_bytes)
                    rtt3=rtt
                    recv_bytes3=recv_bytes
                    send_bytes3=send_bytes
                if rslot=="4":
                    if connected=='yes':
                        st4.update(timestamp, ip, recv_bytes, send_bytes)
                    rtt4=rtt
                    recv_bytes4=recv_bytes
                    send_bytes4=send_bytes

        rtt_list1.append(int(rtt1))
        rtt_list2.append(int(rtt2))
        rtt_list3.append(int(rtt3))
        rtt_list4.append(int(rtt4))
        recv_bytes_list1.append(int(recv_bytes1))
        recv_bytes_list2.append(int(recv_bytes2))
        recv_bytes_list3.append(int(recv_bytes3))
        recv_bytes_list4.append(int(recv_bytes4))
        send_bytes_list1.append(int(send_bytes1))
        send_bytes_list2.append(int(send_bytes2))
        send_bytes_list3.append(int(send_bytes3))
        send_bytes_list4.append(int(send_bytes4))

    if found==0:
        rtt_list1.append(int(rtt1))
        rtt_list2.append(int(rtt2))
        rtt_list3.append(int(rtt3))
        rtt_list4.append(int(rtt4))
        recv_bytes_list1.append(int(recv_bytes1))
        recv_bytes_list2.append(int(recv_bytes2))
        recv_bytes_list3.append(int(recv_bytes3))
        recv_bytes_list4.append(int(recv_bytes4))
        send_bytes_list1.append(int(send_bytes1))
        send_bytes_list2.append(int(send_bytes2))
        send_bytes_list3.append(int(send_bytes3))
        send_bytes_list4.append(int(send_bytes4))

        st_output_all()
        st_output_delta_all()
        #st_output_alldelta_all()
        st_output_broken_all()
        st_init_all()
        print(timestamp, 'stat reset type4 pid not found', expect_pid)
        stRouter.update(timestamp, 4)

    print("")

def stat_ftp_traffic():
    global ts,recv_bytes_list, send_bytes_list
    print('')
    print('stat_ftp original ts, recv, send', len(ts), len(recv_bytes_list), len(send_bytes_list))
    recv_delta=[]
    send_delta=[]
    for i in range(len(recv_bytes_list)):
        #send_bytes_list1[i] = 0.8*(send_bytes_list1[i+1] - send_bytes_list1[i])/1024.0/1024.0
        if i!=0:
            delta_r=(recv_bytes_list[i] - recv_bytes_list[i-1])/1024.0/1024.0
            if delta_r<1.0:
                recv_delta.append(0.0)
            else:
                recv_delta.append(delta_r)

            delta_s=(send_bytes_list[i] - send_bytes_list[i-1])/1024.0/1024.0
            if delta_s<1.0:
                send_delta.append(0.0)
            else:
                send_delta.append(delta_s)
    recv_delta.append(0.0)
    send_delta.append(0.0)
    print('stat_ftp delta ts, recv, send', len(ts), len(recv_delta), len(send_delta))

    ts_recv_sum=[]
    recv_sum=[]
    recv_duration=[]
    ts_send_sum=[]
    send_sum=[]
    send_duration=[]

    recv_s=0
    send_s=0
    recv_count=0
    send_count=0
    for i in range(len(recv_delta)):
        if recv_delta[i]!=0:
            if recv_s==0:
                ts_recv_sum.append(ts[i])
            recv_s += recv_delta[i]
            recv_count += 1
        else:
            if recv_s!=0:
                recv_sum.append(recv_s)
                recv_s=0
                recv_duration.append(recv_count)
                recv_count=0

        if send_delta[i]!=0:
            if send_s==0:
                ts_send_sum.append(ts[i])
            send_s += send_delta[i]
            send_count += 1
        else:
            if send_s!=0:
                send_sum.append(send_s)
                send_s=0
                send_duration.append(send_count)
                send_count=0

    print('recv_sum (upload traffic)')
    for i in range(len(recv_sum)):
        print(ts_recv_sum[i], recv_duration[i], "{:.2f} Mbytes".format(recv_sum[i]), "{:.2f} Mbps".format(0.8*recv_sum[i]/recv_duration[i]))
    print('send_sum (download traffic)')
    for i in range(len(send_sum)):
        print(ts_send_sum[i], send_duration[i], "{:.2f} Mbytes".format(send_sum[i]), "{:.2f} Mbps".format(0.8*send_sum[i]/send_duration[i]))

def init_global():
    global ts
    global st,st1,st2,st3,st4, last_duration,last_router_ip
    global t, rtt_list1, rtt_list2, rtt_list3, rtt_list4
    global recv_bytes_list, recv_bytes_list1, recv_bytes_list2, recv_bytes_list3, recv_bytes_list4
    global send_bytes_list, send_bytes_list1, send_bytes_list2, send_bytes_list3, send_bytes_list4
    global router_reset
    global stRouter

    last_duration=0
    last_router_ip='0'
    st=Stat()
    st1=Stat()
    st2=Stat()
    st3=Stat()
    st4=Stat()
    stRouter=StatRouter()

    router_reset=0

    ts=[]
    count=0
    t=[]
    rtt_list1=[]
    rtt_list2=[]
    rtt_list3=[]
    rtt_list4=[]

    recv_bytes_list=[]
    send_bytes_list=[]

    recv_bytes_list1=[]
    recv_bytes_list2=[]
    recv_bytes_list3=[]
    recv_bytes_list4=[]
    send_bytes_list1=[]
    send_bytes_list2=[]
    send_bytes_list3=[]
    send_bytes_list4=[]

def stat_xml(in_filename, expect_pid, begin_ts, end_ts):
    global stRouter
    global current_ts
    global ts
    global t
    global last_duration
    global last_router_ip
    global st, st1, st2, st3, st4, stRouter
    global router_reset
    global count
    global rtt_list1, rtt_list2, rtt_list3, rtt_list4
    global recv_bytes_list, recv_bytes_list1, recv_bytes_list2, recv_bytes_list3, recv_bytes_list4
    global send_bytes_list, send_bytes_list1, send_bytes_list2, send_bytes_list3, send_bytes_list4

    init_global()

    with open(in_filename) as input_file:
        content = input_file.read()
        #lines = input_file.read().splitlines()
    input_file.close()

    begin_label=0


    max_rtt=2000
    max_recv=5000
    max_send=5000

    #expect_pid="0xF7B6220C5054999B" #hebo
    #expect_pid="0xB28EA0078258902D" #william
    #expect_pid="0x9EB8DB175E1521EC" #chad

    title_ts = begin_ts + ' ~ ' + end_ts

    pos=0
    pos_root_beg=0
    count=0
    new_begin_ts = begin_ts
    st_set_all_begin_ts(new_begin_ts)
    new_end_ts = end_ts
    while pos_root_beg!=-1:
        pos=content.find('2020-', pos)
        pos_line=content.find('\n', pos)
        timestamp=''
        if pos!=-1 and pos_line!=-1 and pos_line>pos:
            timestamp=content[pos:pos_line]
        pos_root_beg=content.find('<root>', pos)
        pos_root_end=content.find('</root>', pos)

        if begin_label==0 and timestamp.find(begin_ts,0)==0:
            stRouter.update(timestamp, 0)
            begin_label=1
            new_begin_ts = timestamp
            st_set_all_begin_ts(new_begin_ts)
            print('begin change', new_begin_ts, ' ~ ', new_end_ts)
        if begin_label==1 and timestamp.find(end_ts,0)==0:
            begin_label=0
            stRouter.update(timestamp, 9)
            new_end_ts = timestamp
            print('end confirm', new_begin_ts, ' ~ ', new_end_ts)
            print('end confirm', new_begin_ts, ' ~ ', new_end_ts, file=sys.stderr)
            break

        if begin_label==1:
            print(timestamp) #(pos, pos_line, pos_root_beg, pos_root_end)
            if pos_root_beg!=-1 and pos_root_end!=-1 and pos_root_end>pos_root_beg:
                one_xml=content[pos_root_beg:pos_root_end+7]
                current_ts = timestamp
                get_status(timestamp, one_xml, count, expect_pid)
                count=count+1
            st_output_all()
            print("")

        pos=pos_root_end+7

    #st_output_all()
    st_output_delta_all()
    st_output_alldelta_all()
    st_output_broken_all()

    print("")
    stRouter.output()

    print('')
    print('draw')

    #plt.figure(1)
    #plt.figure(figsize=(12.8, 9.6))
    plt.figure()
    plt.rcParams['savefig.dpi'] = 200 #图片像素
    plt.rcParams['figure.dpi'] = 200 #分辨率
    #plt.figure(figsize=(28.8, 17.28))
    plt.figure(figsize=(14.4, 8.64))
    ax1 = plt.subplot(4,1,1)
    plt.title(title_ts)
    draw(title_ts,'rtt', 'ms', max_rtt, t, rtt_list1, rtt_list2, rtt_list3, rtt_list4)

    ax4 = plt.subplot(4,1,4)
    draw(title_ts,'download accumulate bytes', 'bytes', max_recv, t, send_bytes_list1, send_bytes_list2, send_bytes_list3, send_bytes_list4)
    #draw(title_ts,'upload accumulate bytes', 'bytes', max_send, t, recv_bytes_list1, recv_bytes_list2, recv_bytes_list3, recv_bytes_list4)

    for i in range(len(send_bytes_list1)):
        if i!=(len(send_bytes_list1)-1):
            send_bytes_list1[i] = 0.8*(send_bytes_list1[i+1] - send_bytes_list1[i])/1024.0/1024.0
            send_bytes_list2[i] = 0.8*(send_bytes_list2[i+1] - send_bytes_list2[i])/1024.0/1024.0
            send_bytes_list3[i] = 0.8*(send_bytes_list3[i+1] - send_bytes_list3[i])/1024.0/1024.0
            send_bytes_list4[i] = 0.8*(send_bytes_list4[i+1] - send_bytes_list4[i])/1024.0/1024.0

            recv_bytes_list1[i] = 0.8*(recv_bytes_list1[i+1] - recv_bytes_list1[i])/1024.0/1024.0
            recv_bytes_list2[i] = 0.8*(recv_bytes_list2[i+1] - recv_bytes_list2[i])/1024.0/1024.0
            recv_bytes_list3[i] = 0.8*(recv_bytes_list3[i+1] - recv_bytes_list3[i])/1024.0/1024.0
            recv_bytes_list4[i] = 0.8*(recv_bytes_list4[i+1] - recv_bytes_list4[i])/1024.0/1024.0
        else:
            send_bytes_list1[i] = 0
            send_bytes_list2[i] = 0
            send_bytes_list3[i] = 0
            send_bytes_list4[i] = 0

            recv_bytes_list1[i] = 0
            recv_bytes_list2[i] = 0
            recv_bytes_list3[i] = 0
            recv_bytes_list4[i] = 0
    ax2 = plt.subplot(4,1,2)
    draw(title_ts , 'download speed', 'Mbps', max_recv, t, send_bytes_list1, send_bytes_list2, send_bytes_list3, send_bytes_list4)
    ax3 = plt.subplot(4,1,3)
    draw(title_ts , 'upload speed',   'Mbps', max_send, t, recv_bytes_list1, recv_bytes_list2, recv_bytes_list3, recv_bytes_list4)
    plt.savefig(title_ts + ".png")
    plt.close()
    #plt.show()

    stat_ftp_traffic()

def st_set_all_begin_ts(new_begin_ts):
    st.set_begin_ts(new_begin_ts)
    st1.set_begin_ts(new_begin_ts)
    st2.set_begin_ts(new_begin_ts)
    st3.set_begin_ts(new_begin_ts)
    st4.set_begin_ts(new_begin_ts)

def st_output_all():
    st.output("router")
    st1.output("slot1")
    st2.output("slot2")
    st3.output("slot3")
    st4.output("slot4")

def st_output_delta_all():
    print("delta traffic")
    st.output_delta("router")
    st1.output_delta("slot1")
    st2.output_delta("slot2")
    st3.output_delta("slot3")
    st4.output_delta("slot4")

def st_output_alldelta_all():
    print("alldelta traffic")
    st.output_alldelta("router")
    st1.output_alldelta("slot1")
    st2.output_alldelta("slot2")
    st3.output_alldelta("slot3")
    st4.output_alldelta("slot4")

def st_output_broken_all():
    print("broken statistics")
    st.output_broken("router")
    st1.output_broken("slot1")
    st2.output_broken("slot2")
    st3.output_broken("slot3")
    st4.output_broken("slot4")

def st_init_all():
    st.__init__()
    st1.__init__()
    st2.__init__()
    st3.__init__()
    st4.__init__()

def draw(title_ts, title, ylbl,ymax, t,a,b,c,d):
    #plt.figure()
    max_a=0
    max_b=0
    max_c=0
    max_d=0
    print('len ', len(t), len(a), len(b), len(c), len(d))
    # red,blue,green,cyan,magenta,black,white,yellow
    if len(a):
        plt.plot(t,a, linewidth='1', color="red", label=title+'1')
        max_a=max(a)
    if len(b):
        plt.plot(t,b, linewidth='1', color="cyan", label=title+'2')
        max_b=max(b)
    if len(c):
        plt.plot(t,c, linewidth='1', color="green", label=title+'3')
        max_c=max(c)
    if len(d):
        plt.plot(t,d, linewidth='1', color="magenta", label=title+'4')
        max_d=max(d)
    if ylbl=='bps':
        e=np.array(a)+np.array(b)+np.array(c)+np.array(d)
        plt.plot(t,e, linewidth='1', color="black", label=title+'_router')

    #https://stackoverflow.com/questions/31193976/how-to-use-matplotlib-set-yscale/31194029
    if ylbl=='bytes':
        plt.yscale('log')
    if ylbl=='ms' or ylbl=='Mbps':
        plt.legend(loc='best')
    #plt.title(title_ts + '\nrouter '+ title)
    plt.xlabel('10s')
    plt.ylabel(ylbl)

    max_y=max(max_a,max_b,max_c,max_d)
    if ylbl=='ms':
        plt.ylim(0, 2000)
    elif ylbl=='Mbps':
        plt.ylim(0, 25)
    else:
        print(title, 'max_y', max_y)
        #plt.ylim(0, max_y)
    #plt.ylim(0, ymax)

    plt.xlim(0, len(t))
    plt.axhline(0)

    #plt.savefig(title_ts +  ' ' + title + ".png")
    #plt.show()

if __name__ == "__main__":
    if len(sys.argv)>5 or len(sys.argv)<2:
        print("Usage: ")
        print("python readfile.py datfile [begin_date] [end_date]")
        sys.exit()

    now_a = datetime.datetime.now()
    print("stat date ", sys.argv[3], sys.argv[4], file=sys.stderr)

    in_filename = sys.argv[1]
    if len(sys.argv)==4:
        end_ts= ''
    elif len(sys.argv)==3:
        end_ts= ''
        begin_ts='2020-04'
    elif len(sys.argv)==2:
        end_ts= ''
        begin_ts='2020-04'
        expect_pid="0xB28EA0078258902D" #william
    else:
        begin_ts=sys.argv[3]
        end_ts=  sys.argv[4]
        expect_pid=sys.argv[2]

    stat_xml(in_filename, expect_pid, begin_ts, end_ts)

    now_b = datetime.datetime.now()
    print("cost time  ", now_b-now_a, file=sys.stderr)
    print("", file=sys.stderr)

