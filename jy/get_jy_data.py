import socket
import time
import json
from struct import unpack
from common_model import CommonModel
common_model = CommonModel()


class V2rSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def myreceive(self):
        while True:
            data = self.sock.recv(65535)
            if unpack('<H', data[:2])[0] == 23123:  #5A53转为10进制
                if unpack('<B', data[2: 3])[0] == 48:
                    """
                    车辆信息上报
                    """
                    obj_len = unpack('<H', data[8: 10])[0]
                    if obj_len:
                        device_id = unpack('<H', data[5: 7])[0]
                        # print("device_id", device_id)
                        batch_dict = {}

                        for i in range(obj_len):
                            single_dict = {}
                            x = unpack('<H', data[10+8*i: 10+8*i+2])[0] * 0.1
                            single_dict["x"] = x
                            # print("x", x)
                            y = unpack('<H', data[10 + 8 * i + 2: 10 + 8 * i + 4])[0] * 0.1
                            single_dict["y"] = y
                            # print("y", y)
                            speed = unpack('<B', data[10 + 8 * i + 4: 10 + 8 * i + 5])[0]
                            # print('speed:', speed)
                            single_dict["speed"] = speed
                            lane = unpack('<B', data[10 + 8 * i + 5: 10 + 8 * i + 6])[0]
                            # print(lane)
                            single_dict["lane"] = lane
                            length = unpack('<B', data[10 + 8 * i + 6: 10 + 8 * i + 7])[0] * 0.1
                            # print(length)
                            single_dict["length"] = length
                            target_id = unpack('<B', data[10 + 8 * i + 7: 10 + 8 * i + 8])[0]
                            # print("target_id", target_id)
                            single_dict["target_id"] = target_id

                            single_dict = json.dumps(single_dict)
                            batch_dict[target_id] = single_dict
                        batch_dict["device_id"] = device_id
                        print(batch_dict ,'-----------dic')
                        batch_dict = json.dumps(batch_dict)
                        # b = eval(batch_dict)
                        # a = json.loads(batch_dict)
                        # print(batch_dict, type(batch_dict))
                        print(len(batch_dict), obj_len)
                        common_model.submit_event(batch_dict)

                        # print(batch_dict)
                        print("*"*30)
                        time.sleep(1)


                        #     with open("data.txt", "a") as f:
                        #         f.write(str(x)+"; "+ str(y)+"; "+str(speed)+"; "+str(lane)+"; "+str(length)+"; "+str(id)+"\n")
                        # with open("data.txt", "a") as f:
                        #     f.write("\n")




if __name__ == '__main__':
    s = V2rSocket()
    s.connect('192.168.1.123', 6000)
    s.myreceive()

"""
1. 安装在道路一侧，左右两侧能识别的范围？
2. 线圈设置参数； 设备信息设置； 告警事件不可设置； 
3. 告警信息上报 间隔1s接收 信息是当前的？
"""
