# _*_ coding: UTF-8 _*_
# Author LBK
from consumer import Consumer
import threading

con = Consumer("raw")
plate_c = Consumer("plate")


if __name__ == "__main__":

    t1 = threading.Thread(target=con.receive_msg_mq, args=("raw", ))
    t1.start()

    t2 = threading.Thread(target=plate_c.receive_msg_mq, args=("plate", ))
    t2.start()

    print("Done")
