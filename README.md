# router_scripts
scripts for router

# Usage

# get server status per 10 seconds and save to file
./get_status.sh SERVER_IP

example:
./get_status.sh 47.115.122.110
which will produce a file name status_47.115.122.110.xml

# output server status statistics
./readfile_server.py SERVER_STATUS_FILE ROUTER_PID BEGIN_DATE END_DATE > OUTPUT_FILE

example:
./readfile_server.py status_47.115.122.110.xml 0x9F37E8B01B37F838 2020-12-01-15-28-45 2020-12-01-15-36-58 > out_47.115.122.110

which will also output to stderr:
stat date  2020-12-01-15-28-45 2020-12-01-15-36-58
end confirm 2020-12-01-15-28-45  ~  2020-12-01-15-36-58
router recv_bytes 85.987 Mbytes send_bytes 74.297 Mbytes
slot1 recv_bytes 0.000 Mbytes send_bytes 0.000 Mbytes
slot2 recv_bytes 0.000 Mbytes send_bytes 0.000 Mbytes
slot3 recv_bytes 12.035 Mbytes send_bytes 2.043 Mbytes
slot4 recv_bytes 73.952 Mbytes send_bytes 72.252 Mbytes
cost time   0:00:01.533423

# output server status statistics day by day
example:
./calltest.py status_47.115.122.110.xml 0x9F37E8B01B37F838 2020-12-01-15-28-45 2020-12-01-15-36-58 > out_47.115.122.110

which will also output to stderr:

