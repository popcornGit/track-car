#coding:utf-8
from types import DynamicClassAttribute
import logging
import json


class MySQLdb(object):
    # def __init__(self, charset='utf8'):
    #     print("**************")
    #     self.host = "192.168.1.241"
    #     self.port = 3872
    #     self.user = "root"
    #     self.password = "6E6Zl4cy0z5phqjL"
    #     # self.database = "voice_control"
    #     self.database = "lidar"
    #     self.charset = charset
    #     try:
    #         self.connect()
    #     except Exception as e:
    #         logging.getLogger("error.log").error(e)

    def __init__(self, charset='utf8'):
        print("**************")
        self.host = "127.0.0.1"
        self.port = 23306
        self.user = "root"
        self.password = "XE1gPm2QfqxbERMp"
        self.database = "event_db"
        self.charset = charset
        try:
            self.connect()
        except Exception as e:
            logging.getLogger("error.log").error(e)

    def connect(self):
        # self.conn = pymysql.connect(host=self.host,
        #                             port=self.port,
        #                             user=self.user,
        #                             password=self.password,
        #                             database=self.database)
        self.cur = self.conn.cursor()

    def insert(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print("e", e)
            # logging.getLogger("error.log").error(e)
        # finally:
        #     self.cur.close()
        #     self.conn.close()

    def search(self, sql):
        try:
            data = self.cur.execute(sql)
            data = self.cur.fetchall()
            return data
        except Exception as e:
            print("e", e)


def get_data(db_id, car_ID_list):

    db = MySQLdb()
    sql = "select * from target_track where id = '{}'".format(db_id)
    data = db.search(sql)

    key_id = data[0][0]
    create_time = data[0][2]

    data_test = data[0][1]
    data_test = data_test[2:len(data_test) - 1].split(r'", "')
    data_test = [item.split(r'": "') for item in data_test]
    data_test[-1] = data_test[-1][0].split(r'": ')
    
    car_list = [eval(item[1]) for item in data_test[:-1]]
    for item in car_list:
        item.update({"create_time": create_time})

    device_id = int(data_test[-1][1])

    return key_id, [car_list], device_id

def update_view_area(leida_list, view_area, non_view_area, car_ID_list):
    # TODO 判断是否是盲区车
    non_view_car = TODO = 1

    # 遍历每一个雷达
    for leida_i in range(len(leida_list)):
        # 遍历每一辆车
        for car in leida_list[leida_i]:
            # 如果该车不处于上一秒的可视范围
            if car["target_id"] not in view_area[leida_i]:
                # 如果是新车
                if non_view_car or leida_i == 0:
                    car["car_ID"] = str(leida_i+1) + "-" + str(car["lane"]) + "-" + str(car_ID_list[leida_i])
                    car_ID_list[leida_i] += 1
                # 如果是前一个雷达的出来的车
                else:
                    pop_car = non_view_area[leida_i-1][car["lane"]].pop(0)
                    car["car_ID"] = pop_car["create_time"]
                # 更新到这一秒的可视范围
                view_area[leida_i][car["target_id"]] = car
            # 如果该车处于上一秒的可视范围, 则更新时间
            else:
                view_area[leida_i][car["target_id"]]["create_time"] = car["create_time"]

def update_non_view_area(leida_list, view_area, non_view_area):
    # 遍历每一个雷达
    for leida_i in range(len(leida_list)):

        # 时间
        new_time = 0

        # 遍历每一辆车, 更新时间
        for car in leida_list[leida_i]:
            new_time = car["create_time"] if car["create_time"] > new_time else new_time
        
        # 找出差集
        disappear_cars = []
        for car in leida_list[leida_i]:
            if car["create_time"] < new_time:
                disappear_cars.append([car["y"], car])
                # 从可视区域删除该车
                view_area[leida_i].pop(car['target_id'])

        # 按照距离存入non_view_area
        disappear_cars.sort(reverse=True)
        for _, car in disappear_cars:
            # 如果不存在该车道
            non_view_area[leida_i][car["lane"]] = [car]


if __name__ == "__main__":

    num_leida = 10  # 雷达数量

    view_area = [{} for i in range(num_leida)]  # 每个雷达的可视区域维护一个列表
    non_view_area = [{} for i in range(num_leida-1)]  # 每个盲区维护一个列表
    car_ID_list = [1 for i in range(num_leida)]  # 每个雷达自编ID

    for db_id in range(1, 1001):
        key_id, leida_list, device_id = get_data(db_id, car_ID_list)
        update_view_area(leida_list, view_area, non_view_area, car_ID_list)
        update_non_view_area(leida_list, view_area, non_view_area)

    print("a")
