# _*_ coding: UTF-8 _*_
# Author LBK
import json


class Track(object):
    def __init__(self, n_line, ip_list):
        self.car_matrix = [[[] for j in range(len(ip_list))] for i in range(n_line)]
        self.no_view_matrix = [[[] for j in range(len(ip_list))] for i in range(n_line)]
        self.last_cleaned_packages = None

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

        with open("20220311_48.txt", "r") as f:
            for line in f.readlines():
                data = json.loads(line)

                if full_flag and time_stamp != data["time_stamp"]:
                    break

                idx = ip_index_dict[data["ip"]]
                first_package[idx] = data
                first_package_set.add(data["ip"])

                if len(first_package_set) == len(ip_list):
                    time_stamp = int(data["time_stamp"])
                    full_flag = True

        return first_package, time_stamp

    def init_car_matrix(self):
        packages = self.first_package
        cleaned_packages = self.clean(packages)
        self.last_cleaned_packages = cleaned_packages

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

            # 过滤数据中车道为4的车辆
            pop_list = []
            for i in range(len(tmp)):
                if tmp[i]["lane"] == 4:
                    pop_list.insert(0, i)

            for i in pop_list:
                tmp.pop(i)

            cleaned_package.append(tmp[:end])
        return cleaned_package

    def process(self):
        time_stamp = self.time_stamp
        interval_package_dict = {}

        with open("20220311_48.txt", "r") as f:
            for line in f.readlines():

                data = json.loads(line)

                data["time_stamp"] = int(data["time_stamp"])

                if data["time_stamp"] > time_stamp:
                    time_stamp = data["time_stamp"]
                    self.track_car(interval_package_dict)
                    interval_package_dict = {}

                interval_package_dict[data["ip"]] = data

    def track_car(self, interval_package):
        packages = [{} for i in ip_list]
        for i in range(len(ip_list)):
            if interval_package.get(ip_list[i], None):
                packages[i] = interval_package[ip_list[i]]

        cleaned_packages = self.clean(packages)

        is_add_result = self.is_add(self.last_cleaned_packages, cleaned_packages)

        self.lane_add_car(is_add_result)

    def is_add(self, last_cleaned_packages, cleaned_packages):
        is_add_result = [[0 for j in range(len(ip_list))] for i in range(n_line)]
        for i in range(len(cleaned_packages)):

            tmp = [{}, {}, {}, 10000.0, 10000.0, 10000.0]

            for car in last_cleaned_packages[i]:
                tmp[car["lane"]-1][car["obj_id"]] = car["y"]
                if float(car["y"]) < tmp[car["lane"]-1+3]:
                    tmp[car["lane"] - 1 + 3] = float(car["y"])

            for car in cleaned_packages[i]:
                if float(car["y"]) < tmp[car["lane"]-1+3] or car["obj_id"] not in tmp[car["lane"]-1]:
                    is_add_result[car["lane"]-1][i] += 1

        self.last_cleaned_packages = cleaned_packages

        return is_add_result

    def lane_add_car(self, param):
        # 从哪儿新增
            # 同车道
            # 盲区
        for radar in range(len(param[0])):
            for lane in range(len(param)):
                print(param[lane][radar])
                for car in range(param[lane][radar]):
                    if self.no_view_matrix[lane][radar]:
                        self.car_matrix[lane][radar].insert(0, self.no_view_matrix[lane][radar].pop(-1))
                    else:
                        self.car_matrix[lane][radar].insert(0, str(lane+1) + "-" + str(self.lane_cars[lane]))
                        self.lane_cars[lane] += 1

                # 车辆进入盲区
                num_car_into_nonview = len(self.car_matrix[lane][radar])
                for car in self.last_cleaned_packages[radar]:
                    if car["lane"]-1 == lane:
                        num_car_into_nonview -= 1

                for i in range(num_car_into_nonview):
                    if radar < len(ip_list) - 1:
                        self.no_view_matrix[lane][radar+1].append(self.car_matrix[lane][radar].pop(-1))
                    else:
                        self.car_matrix[lane][radar].pop(-1)

                # print(self.last_cleaned_packages)
                # print(self.car_matrix)


if __name__ == "__main__":
    # 启动配置
    ip_list = ['44.49.76.165', '44.49.76.166', '44.49.76.167', '44.49.76.168', '44.49.76.169', '44.49.76.170',
               '44.49.76.171', '44.49.76.172', '44.49.76.173', '44.49.76.174']
    n_line = 3

    # 实现类
    trace = Track(n_line, ip_list)
    trace.process()
    print("Done")
