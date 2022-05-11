# _*_ coding: UTF-8 _*_
# Author LBK
import json
import logging
import uuid
import time

import producer
prod_ea = producer.Producer()

import producer_zl
prod_zl = producer_zl.Producer()

from logger import create_logger
create_logger()


class Track(object):

    def __init__(self, n_line, ip_list):
        # 车牌缓冲区
        # 可以取 第 x 雷达,第 x 车道 的车牌信息
        self.plate_matrix = [[[] for j in range(n_line)] for i in range(len(ip_list))]

        # 每条车道的进入车辆数
        self.lane_cars = [0, 0, 0]

        self.ip_list = ip_list
        self.n_line = n_line

        self.new_one_data = {}

        self.time = [0 for radar in range(len(self.ip_list))]
        self.tof = [0 for radar in range(len(self.ip_list))]

        self.log_num = 0

        self.send_flag = [0 for radar in range(len(self.ip_list))]

    def ct_handle(self, ch, method, properties, body):
        """
        车辆跟踪的负责人
        :param:
        :return:
        """
        # 1.收集 新数据
        self.new_one_data = json.loads(body)
        # print(self.new_one_data)

        if self.new_one_data["ip"] in self.ip_list:

            logging.getLogger("error.log").error("=" * 20 + str(self.log_num) + "=" * 20 + self.new_one_data["ip"])
            logging.getLogger("info.log").info("=" * 20 + str(self.log_num) + "=" * 20 + self.new_one_data["ip"])
            self.log_num += 1

            # 2.清理 新数据
            self.clean()

            # 3.对新数据进行跟踪
            self.process()

    def plate_handle(self, ch, method, properties, body):
        """
        处理车牌的负责人
        """
        plate_data = json.loads(body)
        # 绑定 车牌
        for lane in range(len(self.plate_matrix[0])):
            for car_idx in range(len(self.plate_matrix[0][lane])):
                if self.plate_matrix[0][lane][car_idx]["obj_id"] == plate_data["id"]:
                    self.plate_matrix[0][lane][car_idx]["car_plate"] = plate_data["car_plate"]
                    self.plate_matrix[0][lane][car_idx]["obj_type"] = plate_data["obj_type"]
                    break

    def clean(self):
        """
        预处理车辆, 并排序
        """
        cleaned_data = [[], [], []]

        for car in self.new_one_data["value"]:
            if car["lane"] in [1, 2, 3] and car["y"] <= 160.0:
                cleaned_data[car["lane"]-1].append(car)

        for i in range(len(cleaned_data)):
            cleaned_data[i].sort(key=lambda item: float(item["y"]))

        self.new_one_data["cleaned_car"] = cleaned_data

        # 处理时间
        radar = self.ip_list.index(self.new_one_data["ip"])
        self.tof[radar] = self.new_one_data["time_stamp"] - self.time[radar]
        self.tof[radar] = 0.5 if self.tof[radar] < 0 else self.tof[radar]
        self.time[radar] = self.new_one_data["time_stamp"]

    def process(self):

        radar = self.ip_list.index(self.new_one_data["ip"])
        # print(radar)

        car_buff = self.new_one_data["cleaned_car"]
        plate_buff = self.plate_matrix[radar]

        # 打log
        logging.getLogger("info.log").info("=" * 20 + "car_buff" + "=" * 20)
        for i in car_buff:
            logging.getLogger("info.log").info(i)

        logging.getLogger("info.log").info("=" * 20 + "plate_buff" + "=" * 20)
        for i in plate_buff:
            logging.getLogger("info.log").info(i)

        car_tmp = [[0 for j in range(len(car_buff[i]))] for i in range(len(car_buff))]
        plate_tmp = [[0 for j in range(len(plate_buff[i]))] for i in range(len(plate_buff))]

        car_tmp, plate_tmp = self.current_car_1(car_buff, plate_buff, car_tmp, plate_tmp)
        # car_tmp, plate_tmp = self.change_car_2(car_buff, plate_buff, car_tmp, plate_tmp)
        car_tmp = self.new_car_3(car_tmp)
        plate_tmp = self.disappear_car_4(plate_tmp, plate_buff)
        plate_tmp = self.fake_car_5(plate_tmp)
        # print(car_tmp)
        # print(plate_tmp)

        # 打log
        logging.getLogger("info.log").info("=" * 20 + "car_tmp" + "=" * 20)
        for i in car_tmp:
            logging.getLogger("info.log").info(i)

        logging.getLogger("info.log").info("=" * 20 + "plate_tmp" + "=" * 20)
        for i in plate_tmp:
            logging.getLogger("info.log").info(i)

        plate_buff, plate_tmp = self.process_5(plate_buff, plate_tmp)

        plate_buff = self.process_4(plate_buff, plate_tmp)

        plate_buff = self.process_1_2(plate_buff, plate_tmp, car_buff)

        if self.new_one_data["ip"].endswith("211"):
            plate_buff = self.process_3(car_tmp, plate_buff, car_buff)

        self.data_resort(plate_buff)
        
        self.show_time(len(self.ip_list))

        self.show_front(4)

    def current_car_1(self, car_buff, plate_buff, car_tmp, plate_tmp):
        # print(car_buff)
        # print(plate_buff)
        # print(car_tmp)
        # print(plate_tmp)
        for lane in range(len(plate_buff)):
            for plate_idx in range(len(plate_buff[lane])):
                if plate_tmp[lane][plate_idx]:
                    continue
                for car_idx in range(len(car_buff[lane])):
                    if car_tmp[lane][car_idx]:
                        continue
                    elif 50.0 > car_buff[lane][car_idx]["y"] - plate_buff[lane][plate_idx]["y"] > 0:
                        car_tmp[lane][car_idx] = 1
                        plate_tmp[lane][plate_idx] = (lane, car_idx)
                        break

        return car_tmp, plate_tmp

    def change_car_2(self, car_buff, plate_buff, car_tmp, plate_tmp):
        for plate_lane in range(len(plate_buff)):
            for plate_idx in range(len(plate_buff[plate_lane])):
                if plate_tmp[plate_lane][plate_idx]:
                    continue
                else:
                    for car_lane in range(len(car_buff)):
                        if plate_tmp[plate_lane][plate_idx]:
                            break
                        for car_idx in range(len(car_buff[car_lane])):
                            if car_tmp[car_lane][car_idx]:
                                continue
                            elif 0 < car_buff[car_lane][car_idx]["y"] - plate_buff[plate_lane][plate_idx]["y"] < 15.0\
                                    and plate_lane - car_lane in [-1, 1]:
                                car_tmp[car_lane][car_idx] = 2
                                plate_tmp[plate_lane][plate_idx] = (car_lane, car_idx)
                                break
        return car_tmp, plate_tmp

    def new_car_3(self, car_tmp):
        for car_lane in range(len(car_tmp)):
            for car_idx in range(len(car_tmp[car_lane])):
                if not car_tmp[car_lane][car_idx]:
                    car_tmp[car_lane][car_idx] = 3
                else:
                    break

        return car_tmp

    def disappear_car_4(self, plate_tmp, plate_buff):
        for plate_lane in range(len(plate_tmp)):
            for plate_idx in range(len(plate_tmp[plate_lane])):
                if plate_tmp[plate_lane][plate_idx]:
                    continue
                elif plate_buff[plate_lane][plate_idx]["y"] > 140.0:
                    plate_tmp[plate_lane][plate_idx] = 4

        return plate_tmp

    def fake_car_5(self, plate_tmp):
        for plate_lane in range(len(plate_tmp)):
            for plate_idx in range(len(plate_tmp[plate_lane])):
                if plate_tmp[plate_lane][plate_idx]:
                    continue
                else:
                    plate_tmp[plate_lane][plate_idx] = 5

        return plate_tmp

    def process_1_2(self, plate_buff, plate_tmp, car_buff):

        for plate_lane in range(len(plate_buff)):
            for plate_idx in range(len(plate_buff[plate_lane])):
                if plate_tmp[plate_lane][plate_idx] not in [4, 5]:
                    car_idx = plate_tmp[plate_lane][plate_idx]

                    plate_buff[plate_lane][plate_idx]["x"] = car_buff[car_idx[0]][car_idx[1]]["x"]
                    plate_buff[plate_lane][plate_idx]["y"] = car_buff[car_idx[0]][car_idx[1]]["y"]
                    plate_buff[plate_lane][plate_idx]["speed"] = car_buff[car_idx[0]][car_idx[1]]["speed"]
                    plate_buff[plate_lane][plate_idx]["lane"] = car_buff[car_idx[0]][car_idx[1]]["lane"]

        return plate_buff

    def process_3(self, car_tmp, plate_buff, car_buff):

        radar = self.ip_list.index(self.new_one_data["ip"])

        for car_lane in range(len(car_tmp)):
            for car_idx in range(len(car_tmp[car_lane])):
                if car_tmp[car_lane][car_idx] == 3:

                    plate = str(radar+1) + "-" + str(car_lane) + "-" + str(self.lane_cars[car_lane-1])
                    self.lane_cars[car_lane - 1] += 1
                    car_buff[car_lane][car_idx]["my_id"] = plate

                    my_uuid = str(uuid.uuid1()).upper()
                    car_buff[car_lane][car_idx]["uuid"] = my_uuid

                    time_stamp = self.new_one_data["time_stamp"]
                    time_array = time.localtime(time_stamp)
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
                    car_buff[car_lane][car_idx]["time_stamp"] = time_str

                    car_buff[car_lane][car_idx]["car_plate"] = ""

                    plate_buff[car_lane].insert(0, car_buff[car_lane][car_idx])

        return plate_buff

    def process_4(self, plate_buff, plate_tmp):

        radar = self.ip_list.index(self.new_one_data["ip"])
        tof = self.tof[radar]

        for plate_lane in range(len(plate_buff)):

            pop_list = []

            for plate_idx in range(len(plate_buff[plate_lane])-1, -1, -1):
                if plate_tmp[plate_lane][plate_idx] == 4:
                    speed = plate_buff[plate_lane][plate_idx]["speed"]
                    plate_buff[plate_lane][plate_idx]["y"] += (speed / 3.6) * tof
                    plate_buff[plate_lane][plate_idx]["y"] = round(plate_buff[plate_lane][plate_idx]["y"], 2)

                    plate_buff[plate_lane][plate_idx]["y"] -= 150.0
                    plate_buff[plate_lane][plate_idx]["y"] = round(plate_buff[plate_lane][plate_idx]["y"], 2)

                    pop_list.append(plate_idx)

            for plate_idx in pop_list:
                if radar + 1 == len(self.ip_list):
                    plate_buff[plate_lane].pop(plate_idx)
                else:
                    self.plate_matrix[radar+1][plate_lane].insert(0, plate_buff[plate_lane].pop(plate_idx))

        return plate_buff

    def process_5(self, plate_buff, plate_tmp):

        radar = self.ip_list.index(self.new_one_data["ip"])
        tof = self.tof[radar]

        for plate_lane in range(len(plate_buff)):
            for plate_idx in range(len(plate_buff[plate_lane])):
                if plate_tmp[plate_lane][plate_idx] == 5:

                    speed = plate_buff[plate_lane][plate_idx]["speed"]

                    if plate_buff[plate_lane][plate_idx]["y"] + (speed / 3.6) * tof > 160.0:
                        plate_tmp[plate_lane][plate_idx] = 4
                    else:
                        plate_buff[plate_lane][plate_idx]["y"] += (speed / 3.6) * tof
                        plate_buff[plate_lane][plate_idx]["y"] = round(plate_buff[plate_lane][plate_idx]["y"], 2)


        return plate_buff, plate_tmp

    def data_resort(self, plate_buff):

        radar = self.ip_list.index(self.new_one_data["ip"])
        plate_new_buff = [[] for lane in range(len(plate_buff))]

        for i in range(len(plate_buff)):
            for j in range(len(plate_buff[i])):
                plate_new_buff[plate_buff[i][j]["lane"]-1].append(plate_buff[i][j])

        for lane in range(len(plate_new_buff)):
            plate_new_buff[lane].sort(key=lambda item: float(item["y"]))

        self.plate_matrix[radar] = plate_new_buff

    def show_time(self, n):

        output = [[[] for j in range(self.n_line)] for i in range(len(self.ip_list))]

        for radar in range(len(self.plate_matrix)):
            for lane in range(len(self.plate_matrix[radar])):
                for item in self.plate_matrix[radar][lane]:
                    output[radar][lane].append({"y": item["y"], "plate": item["my_id"]})

        for lane in range(self.n_line):
            tmp = []
            for radar in range(n):
                tmp.append(output[radar][lane])

            logging.getLogger("error.log").error(tmp)

        logging.getLogger("error.log").error("="*50)

    def show_front(self, n):

        if min(self.send_flag) < n - 1:
            radar = self.ip_list.index(self.new_one_data["ip"])
            self.send_flag[radar] += 1
            return

        self.show_ea_zl()

        # 恢复 发送 flag
        self.send_flag = [0 for radar in range(len(self.ip_list))]

    def show_ea_zl(self):
        output = []

        for radar in range(len(self.ip_list)):

            data = self.plate_matrix[radar]
            one = {"ip": self.ip_list[radar]}

            time_stamp = self.new_one_data["time_stamp"]
            time_array = time.localtime(time_stamp)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            one["time_stamp"] = time_str

            value = []

            for lane in range(len(data)):
                for plate_idx in range(len(data[lane])):
                    tmp = {"x": data[lane][plate_idx]["x"],
                           "y": data[lane][plate_idx]["y"],
                           "speed": data[lane][plate_idx]["speed"],
                           "lane": data[lane][plate_idx]["lane"],
                           "obj_id": data[lane][plate_idx]["uuid"],
                           "obj_type": data[lane][plate_idx]["obj_type"],
                           "car_plate": data[lane][plate_idx]["car_plate"]}
                    value.append(tmp)
            if value:
                one["value"] = value

                output.append(one)

        print("output", output)
        prod_ea.send_msg_mq(json.dumps(output))
        prod_zl.send_msg_mq(json.dumps(output))
