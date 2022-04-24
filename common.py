#coding: utf-8
import json
import time
import cv2
import datetime
import random
from model import Model
from producer import Producer
p = Producer()
from logger import create_logger
create_logger()
import logging

class Common(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            obj = super(Common, cls).__new__(cls, *args, **kwargs)
            obj.save_pic = {}    # {"ip": {"pic_name": "xx", "position": []}
            obj.save_video = {}  # {"ip": {"video_name": "xx", "last_time": xx}
            cls.instance = obj
        return cls.instance

    def cap_pic(self, video):
        pics_path = "/home/runone/program/folder/testvideo/radar/pics/"
        cap = cv2.VideoCapture(video[0])
        while True:
            time.sleep(0.2)
            while True:
                ret, frame = cap.read()
                if ret:
                    if Common.instance.save_pic.get(video[1]):
                        pic_info = Common.instance.save_pic.pop(video[1])
                        if pic_info:
                            for index, po in enumerate(pic_info["position"]):
                                x, y = po[0], po[1]
                            #     left_top = (x-1, y-2)
                            #     right_buttom = (x+1, y+2)
                                # cv2.rectangle(frame, left_top, right_buttom, (0, 0, 255), 3)
                                text = "x: " + str(x) + ", y: " + str(y)
                                cv2.putText(frame, text, (200, 200+50*index), cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 255), 2)
                            pic_name = pic_info["pic_name"]
                            frame = cv2.resize(frame, (900, 600))
                            cv2.imwrite(pics_path + pic_name, frame)
                            print("save pic ", pic_name)
                else:
                    logging.getLogger("error.log").error("ip: {}, img_data: {}".format(video[1], Common.instance.save_pic))
                    break

    @classmethod
    def submit(cls, task_id, ip="", vid_path="", now_time=1, event_code=1, submit_type=1, total_num=0, avg_speed=0, single_data=None, batch_dict_data=None, batch_list_data=None):
        if submit_type == 1: # 提交事件
            position = []
            new_ip = ip.replace(".", "_")
            video_name = new_ip + "_" +str(now_time) + ".mp4"
            if Common.instance.save_video.get(ip):
                if now_time - Common.instance.save_video[ip]["last_time"] > 60:
                    Common.instance.save_video[ip]["last_time"] = now_time
                    Common.instance.save_video[ip]["video_name"] = video_name
                    msg = json.dumps({"status": 3, "vid_path": vid_path, "task_id": task_id, "mechine_number": "1", "content": "/testvideo/radar/videos/" + video_name})
                    p.send_msg_mq("common", msg)
                else:
                    video_name = Common.instance.save_video[ip]["video_name"]
            else:
                Common.instance.save_video[ip] = {"last_time": now_time}
                Common.instance.save_video[ip]["video_name"] = video_name
                msg = json.dumps({"status": 3, "vid_path": vid_path, "task_id": task_id, "mechine_number": "1", "content": "/testvideo/radar/videos/"+video_name})
                p.send_msg_mq("common", msg)

            image = new_ip + "_" + str(now_time) + ".png"
            if single_data:
                position.append((int(float(single_data["x"])), int(float(single_data["y"]))))
            elif batch_dict_data:
                for d in batch_dict_data.values():
                    position.append((int(float(d["x"])), int(float(d["y"]))))
            # elif batch_list_data:
            #     for d in batch_list_data:
            #         position.append((int(float(d["x"])), int(float(d["y"]))))
            Common.instance.save_pic[ip] = {"pic_name": image, "position": position}
            new_id = str(task_id).zfill(5)
            alarm_number = "GJA" + new_id + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(100, 999))
            print("ip: ", ip, "event_code: ", event_code, "alarm_number", alarm_number)
            id = Model.submit_event(task_id, event_code, "./testvideo/radar/videos/" + video_name, "./testvideo/radar/pics/" + image, alarm_number)
            # print("position", position)
            print("cls_instance_save_pic", Common.instance.save_pic)
            # p.send_msg_mq("event", json.dumps({"id": id, "task_id": task_id, "total_event": 1, "alarmnumber": alarm_number}))

        elif submit_type == 2:  # 提交统计
            Model.submit_statistics(task_id, total_num, avg_speed)

