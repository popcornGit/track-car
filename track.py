# _*_ coding: UTF-8 _*_
# Author LBK
import json


class Track(object):
    def __init__(self, n_line, ip_list):
        self.car_matrix = [[[] for j in range(len(ip_list))] for i in range(n_line)]
        self.lane_cars = [0, 0, 0]
        # print(self.car_matrix)
        self.first_package, self.time_stamp = self.get_first_package(ip_list)
        self.init_car_matrix()

    def get_first_package(self, ip_list):
        """
        启动看第一眼
        :param ip_list:
        :return:
        """
        time_stamp = 0
        first_package_set = set()
        first_package = [i for i in range(len(ip_list))]  # 初始化 first_package 为 [0 1 2 3 4 5 6 7 8]
        ip_index_dict = {ip_list[i]: i for i in range(len(ip_list))}  # {165:0, 166:1, 168:2 ...}
        full_flag = False

        with open("data113.txt", "r") as f:
            for line in f.readlines():
                data = json.loads(line)

                if full_flag and time_stamp != data["time_stamp"]:
                    break

                idx = ip_index_dict[data["ip"]]
                first_package[idx] = data
                first_package_set.add(data["ip"])

                if len(first_package_set) == len(ip_list):
                    time_stamp = data["time_stamp"]
                    full_flag = True

        return first_package, time_stamp

    def init_car_matrix(self):
        packages = self.first_package
        cleaned_packages = self.clean(packages)

        for i in range(len(cleaned_packages)-1, -1, -1):
            for j in range(len(cleaned_packages[i])-1, -1, -1):
                lane = cleaned_packages[i][j]["lane"]
                self.car_matrix[lane-1][i].insert(0, str(lane)+"-"+str(self.lane_cars[lane-1]))
                self.lane_cars[lane-1] += 1

    def clean(self, packages):
        """
        提取 y, lane, obj_id, 清理超出指定范围的车辆, 并排序
        :param packages:
        :return:
        """
        cleaned_package = []
        for package in packages:
            tmp = []
            for key in package.keys():
                if key not in ["ip", "task_type", "time_stamp"]:
                    tmp.append({})
                    for sub_key in package[key].keys():
                        if sub_key in ["y", "lane", "obj_id"]:
                            tmp[-1][sub_key] = package[key][sub_key]

            tmp.sort(key=lambda item: float(item["y"]))

            end = len(tmp)
            for i in range(len(tmp)):
                if float(tmp[i]["y"]) > 130.0:
                    end = i
                    break

            cleaned_package.append(tmp[:end])
        return cleaned_package

    def process(self):
        time_stamp = self.time_stamp
        interval_package_dict = {}

        with open("data113.txt", "r") as f:
            for line in f.readlines():

                data = json.loads(line)

                if data["time_stamp"] > time_stamp:
                    time_stamp = data["time_stamp"]
                    self.track_car(interval_package_dict)
                    interval_package_dict = {}

                interval_package_dict[data["ip"]] = data

    def track_car(self, interval_package):
        packages = [{} for i in ip_list]
        for i in range(len(ip_list)):
            packages[i] = interval_package[ip_list[i]]

        cleaned_packages = self.clean(packages)
        print(len(interval_package))
        # TODO 需要新增吗?
            # 从哪儿新增
                # 同车道
                # 隔壁车道
                # 盲区
        # TODO 需要删除吗?


if __name__ == "__main__":
    # 启动配置
    ip_list = ['44.49.76.165', '44.49.76.166', '44.49.76.168', '44.49.76.169', '44.49.76.170', '44.49.76.171',
               '44.49.76.172', '44.49.76.173', '44.49.76.174']
    n_line = 3

    # 实现类
    trace = Track(n_line, ip_list)
    trace.process()
