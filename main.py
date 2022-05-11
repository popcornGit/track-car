# _*_ coding: UTF-8 _*_
# Author LBK
from consumer import Consumer
# from producer import Producer
import threading

con = Consumer("raw")
plate_c = Consumer("plate")
# prod = Producer()


if __name__ == "__main__":

    t1 = threading.Thread(target=con.receive_msg_mq, args=("raw", ))
    t1.start()

    t2 = threading.Thread(target=plate_c.receive_msg_mq, args=("plate", ))
    t2.start()

    # t3 = threading.Thread(target=prod.send_msg_mq, args=("a",))
    # t3.start()

    print("Done")
