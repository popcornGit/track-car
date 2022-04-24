# _*_ coding: UTF-8 _*_
# Author LBK
import json
import time
import logging
from logger import create_logger
create_logger()


class Track(object):

    def __init__(self, n_line, ip_list):
        # 3 车道 10雷达可视区
        self.car_matrix = [[[] for j in range(len(ip_list))] for i in range(n_line)]
        # 3 车道 9雷达可视区 第一列凑数
        self.no_view_matrix = [[[] for j in range(len(ip_list))] for i in range(n_line)]
        # 跟上次的所有车辆数据对比，用于确定哪些是新车
        self.last_time_car = {ip:{} for ip in ip_list}

        # 每条车道的进入车辆数
        self.lane_cars = [0, 0, 0]

        self.ip_list = ip_list
        self.n_line = n_line

        self.new_one_data = {}

        self.plate_pool = [{} for ip in ip_list]

        self.change_plate_pool = [{} for ip in ip_list]

        self.time = 0

    def ct_handle(self, ch, method, properties, body):
        """
        车辆跟踪的负责人
        :param:
        :return:
        """
        #1.收集 新数据
        self.get_data(body)
        #2.清理 新数据
        cleaned_data = self.clean(self.new_one_data)
        self.new_one_data["cleaned_data"] = cleaned_data
        # print(self.new_one_data)
        #3.对新数据进行跟踪
        self.track_car()

    def plate_handle(self, ch, method, properties, body):
        """
        处理车牌的负责人
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        plate_data = json.loads(body)
#        if self.plate_pool[0].get([plate_data["id"]], None):
#            self.plate_pool[0][plate_data["id"]] = plate_data["car_plate"]
        print(plate_data)
        print(self.plate_pool[0])

    @staticmethod
    def clean(data):
        """
        提取 y, lane, obj_id, 清理超出指定范围的车辆, 并排序
        :param data:
        :return:
        [{"y":1.0, "lane":2, "obj_id":123}, {}]
        """
        tmp = []

        for key in data.keys():
            if key not in ["ip", "task_type", "time_stamp"]:
                tmp.append({})
                for sub_key in data[key].keys():
                    if sub_key in ["y", "lane", "obj_id"]:
                        tmp[-1][sub_key] = data[key][sub_key]

        tmp.sort(key=lambda item: float(item["y"]))

        # 过滤数据中车道为4的车辆
        pop_list = []
        for i in range(len(tmp)):
            if tmp[i]["lane"] >= 4:
                pop_list.insert(0, i)

        for i in pop_list:
            tmp.pop(i)

        #过滤超过160m的车辆
        end = len(tmp)
        for i in range(len(tmp)):
            if float(tmp[i]["y"]) > 160.0:
                end = i
                break

        cleaned_data = tmp[:end]
        return cleaned_data

    def track_car(self):

        cur, add, sub, change = self.cur_add_sub()
        # print("cur=", cur)
        # print("add=", add)
        # print("sub=", sub)

        self.process(cur, add, sub, change)

    def cur_add_sub(self):
        cur, add, sub, change = [], [], [], []
        tmp = []

        last_car_list = self.last_time_car[self.new_one_data["ip"]]
        #print("="*20,"last_car_list", last_car_list, "="*20)
        for car in self.new_one_data["cleaned_data"]:

            tmp.append(car["obj_id"])

            if car["obj_id"] not in last_car_list and float(car["y"]) < 80.0:
                add.append(self.new_one_data[car["obj_id"]])
            elif car["obj_id"] in last_car_list:
                cur.append(self.new_one_data[car["obj_id"]])
            else:
                change.append(self.new_one_data[car["obj_id"]])

        for car_id in last_car_list:
            if car_id not in tmp:
                sub.append(last_car_list[car_id])

        self.last_time_car[self.new_one_data["ip"]] = {}
       # print(self.new_one_data)
        for car in add:
           # print(self.new_one_data)
            self.last_time_car[self.new_one_data["ip"]][car["obj_id"]] = self.new_one_data[car["obj_id"]]
        for car in cur:
            self.last_time_car[self.new_one_data["ip"]][car["obj_id"]] = self.new_one_data[car["obj_id"]]
        for car in change:
            self.last_time_car[self.new_one_data["ip"]][car["obj_id"]] = self.new_one_data[car["obj_id"]]

        return cur, add, sub, change

    def process(self, cur, add, sub, change):

        radar = self.ip_list.index(self.new_one_data["ip"])

        # 车辆进入盲区
        for car in sub:
            if radar + 1 < len(self.ip_list):
                if 140.0 <= car["y"] <= 160.0:
                    self.no_view_matrix[car["lane"]-1][radar+1].append(self.plate_pool[radar][car["obj_id"]])
                else:
                    self.change_plate_pool[radar][self.plate_pool[radar][car["obj_id"]]] = car["y"]

            self.plate_pool[radar].pop(car["obj_id"])

        # 新增车辆
        for i in range(len(self.car_matrix)):
            self.car_matrix[i][radar] = []

        for car in reversed(add):

            if self.no_view_matrix[car["lane"]-1][radar]:
                plate = self.no_view_matrix[car["lane"]-1][radar].pop(-1)
                self.plate_pool[radar][car["obj_id"]] = plate
                self.car_matrix[car["lane"]-1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})

            elif self.change_plate_pool[radar]:
                y = 100000
                plate = "car_plate"
                for plate_y in self.change_plate_pool[radar].items():
                    if -2 <= car["y"] - plate_y[1] <= y:
                        y = car["y"] - plate_y[1]
                        plate = plate_y[0]
                self.plate_pool[radar][car["obj_id"]] = plate
                self.car_matrix[car["lane"] - 1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                self.change_plate_pool[radar].pop(plate)

            else:
                other_lane = [1,2,3]
                other_lane.remove(car["lane"])
                if self.no_view_matrix[other_lane[0]-1][radar]:
                    plate = self.no_view_matrix[other_lane[0]-1][radar].pop(-1)
                    self.plate_pool[radar][car["obj_id"]] = plate
                    self.car_matrix[car["lane"] - 1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                elif self.no_view_matrix[other_lane[1]-1][radar]:
                    plate = self.no_view_matrix[other_lane[1]-1][radar].pop(-1)
                    self.plate_pool[radar][car["obj_id"]] = plate
                    self.car_matrix[car["lane"] - 1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                else:
                    # self.car_matrix[car["lane"]-1][radar].append(car["obj_id"] +"-"+ str(car["lane"]-1 + 1) +"-"+ str(self.lane_cars[car["lane"]-1]) +"-"+ str(car["y"]))
                    # obj_id: y, 雷达-车道-车次
                    plate = str(radar+1) +"-"+ str(car["lane"]) +"-"+ str(self.lane_cars[car["lane"]-1])
                    self.plate_pool[radar][car["obj_id"]] = plate
                    self.car_matrix[car["lane"]-1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                    self.lane_cars[car["lane"]-1] += 1

        for car in cur:
            self.car_matrix[car["lane"]-1][radar].append({car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})

        for car in change:
            if self.change_plate_pool[radar]:
                y = 100000
                plate = "car_plate"
                for plate_y in self.change_plate_pool[radar].items():
                    if -2 <= car["y"] - plate_y[1] <= y:
                        y = car["y"] - plate_y[1]
                        plate = plate_y[0]
                self.plate_pool[radar][car["obj_id"]] = plate
                self.car_matrix[car["lane"] - 1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                self.change_plate_pool[radar].pop(plate)
            else:
                plate = str(radar + 1) + "-" + str(car["lane"]) + "-" + str(self.lane_cars[car["lane"] - 1])
                self.plate_pool[radar][car["obj_id"]] = plate
                self.car_matrix[car["lane"] - 1][radar].insert(0, {car["obj_id"]: [car["y"], self.plate_pool[radar][car["obj_id"]]]})
                self.lane_cars[car["lane"] - 1] += 1


        if time.time() - self.time >= 1:
            self.time = time.time()
            for i in range(len(self.car_matrix)):
                if 1:
                    logging.getLogger("info.log").info(self.car_matrix[i])
                    print(self.car_matrix[i])
            logging.getLogger("info.log").info("="*80)
            print("="*80)

    def get_data(self, body):

        new_format_data = json.loads(body)

        old_format_data = {"ip": new_format_data["ip"],
                          "time_stamp": new_format_data["time_stamp"]}

        for car in new_format_data["value"]:
           old_format_data[car["obj_id"]] = car

        self.new_one_data = old_format_data


if __name__ == "__main__":
    # 启动配置
    ip_list = ['44.49.76.165', '44.49.76.166', '44.49.76.167', '44.49.76.168', '44.49.76.169', '44.49.76.170',
               '44.49.76.171', '44.49.76.172', '44.49.76.173', '44.49.76.174']
    n_line = 3

    # 实现类
    trace = Track(n_line, ip_list)
