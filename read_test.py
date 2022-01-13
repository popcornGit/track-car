# _*_ coding: UTF-8 _*_
# Author LBK
import json

ip_set = set(
    ['44.49.76.171', '44.49.76.166', '44.49.76.173', '44.49.76.170', '44.49.76.174', '44.49.76.169', '44.49.76.165',
     '44.49.76.172', '44.49.76.168'])
ip_dict = {k: 0 for k in ip_set}
other_ip = []

with open("data113.txt", "r") as f:
    time_stamp = 0
    for line in f.readlines():
        data = json.loads(line)
        if time_stamp < data["time_stamp"]:
            time_stamp = data["time_stamp"]
            # 用于查看连续丢包
            print(ip_dict)
        if data["ip"] in ip_dict:
            ip_dict[data["ip"]] += 1
        else:
            other_ip.append(data["ip"])

v_list = [v for v in ip_dict.values()]
print(v_list)
print(sum(v_list))
print(other_ip)
