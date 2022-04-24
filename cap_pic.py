# _*_ coding: UTF-8 _*_
# Author LBK
import threading
from consumer import Consumer
import cv2
# from common import Common


def cap_pic(video):
    pics_path = "/home/runone/radar/car_track/pictures/"
    cap = cv2.VideoCapture(video[0])
    while True:
        ret, frame = cap.read()
        print("="*30)
        print(ret)
        if ret:
            frame = cv2.resize(frame, (900, 600))
            cv2.imwrite(pics_path + "pic_name.jpg", frame)
            print("save pic ", "done")
        else:
            print("ip: ", video[1])
            break
        break

if __name__ == '__main__':

    videos = [
        ("rtsp://admin:pass9999@44.49.76.74/Streaming/Channels/1", "44.49.76.165"),
        ("rtsp://admin:pass9999@44.49.76.76/Streaming/Channels/1", "44.49.76.166"),
        ("rtsp://admin:pass9999@44.49.76.78/Streaming/Channels/1", "44.49.76.167"),
        ("rtsp://admin:pass9999@44.49.76.80/Streaming/Channels/1", "44.49.76.168"),
        ("rtsp://admin:pass9999@44.49.76.82/Streaming/Channels/1", "44.49.76.169"),
        ("rtsp://admin:pass9999@44.49.76.84/Streaming/Channels/1", "44.49.76.170"),
        ("rtsp://admin:pass9999@44.49.76.86/Streaming/Channels/1", "44.49.76.171"),
        ("rtsp://admin:pass9999@44.49.76.88/Streaming/Channels/1", "44.49.76.172"),
        ("rtsp://admin:pass9999@44.49.76.90/Streaming/Channels/1", "44.49.76.173"),
        ("rtsp://admin:pass9999@44.49.76.92/Streaming/Channels/1", "44.49.76.174")
    ]  # (video, ip)

    cap_pic(videos[0])
    # t1_list = []
    # for v in video:  # v=("rtsp://admin:pass9999@44.49.76.74/Streaming/Channels/1", "44.49.76.165")
    #     t1 = threading.Thread(target=cap_pic, args=(v,))
    #     t1_list.append(t1)
    # for t1 in t1_list:
    #     t1.start()

    # con = Consumer()
    # t2_list = []
    # for i in range(10):
    #     t2 = threading.Thread(target=con.receive_msg_mq)
    #     t2_list.append(t2)
    # for t2 in t2_list:
    #     t2.start()
