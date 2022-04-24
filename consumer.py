#coding: utf-8
import pika
import configupdater
import json
import threading

# 实例化 track_mq 对象
from track_mq import Track
# 启动配置
ip_list = ['44.49.76.165', '44.49.76.166', '44.49.76.167', '44.49.76.168', '44.49.76.169', '44.49.76.170','44.49.76.171', '44.49.76.172', '44.49.76.173', '44.49.76.174']
#ip_list = ["44.49.76.165", "44.49.76.173"]
n_line = 3
# 实现类
trace = Track(n_line, ip_list)
# trace.process()


class Consumer(object):

    def __init__(self, cfg):
        #print("consumer init")
        conf = configupdater.ConfigUpdater()
        conf.read('config.ini', encoding="utf-8")
        self.user = conf['crmq']['user'].value
        self.password = conf['crmq']['password'].value
        self.ip = conf['crmq']['ip'].value
        self.port = int(conf['crmq']['port'].value)
        self.vhost = conf['crmq']['vhost'].value

        if cfg == "plate":
            self.queue = "radar_vehicle_plate"
        else:
            self.queue = conf['crmq']['queue'].value

    def receive_msg_mq(self, cfg):
        """消费mq消息"""
        #try:
        credentials = pika.PlainCredentials(self.user, self.password)
        s_conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.ip, port=self.port, virtual_host=self.vhost, credentials=credentials))
        channel = s_conn.channel()
        if cfg == "raw":
           # print(cfg)
           # print(self.user, self.password, self.ip, self.port, self.vhost, self.queue)
            channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": 5000})
            channel.basic_consume(queue=self.queue, on_message_callback=trace.ct_handle, auto_ack=True)
        else:
           # print(cfg)
           # print(self.user, self.password, self.ip, self.port, self.vhost, self.queue)
            channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": 10000})
            channel.basic_consume(queue=self.queue, on_message_callback=trace.plate_handle, auto_ack=True)

        channel.start_consuming()
        #except Exception as e:
        #    print("receive_msg_mq error: ", e)

    def callback(self, ch, method, properties, body):
        data = json.loads(body)
        print(data, threading.current_thread().name)
        print()


if __name__ == '__main__':

    c = Consumer()
    c.receive_msg_mq()


