#coding: utf-8
import pika
import configupdater
import json
import threading

# 实例化 track_mq 对象
from track_mq_nochange import Track
# 启动配置
ip_list = ["192.168.1.211", "192.168.1.212", "192.168.1.213", "192.168.1.214", "192.168.1.215"]
n_line = 3
# 实现类
trace = Track(n_line, ip_list)


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
        s_conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.ip, port=self.port, virtual_host=self.vhost, credentials=credentials))

        channel = s_conn.channel()

        if cfg == "raw":
            # channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": 60000})
            # channel.basic_consume(queue=self.queue, on_message_callback=trace.ct_handle, auto_ack=True)
            channel.exchange_declare(
                # exchange="radar.vehicle.track.display.fanout",
                exchange="radar.target.info.fanout",
                exchange_type="fanout",
            )

            channel.queue_declare(queue=self.queue, exclusive=True)
            channel.queue_bind(
                # exchange="radar.vehicle.track.display.fanout",
                exchange="radar.target.info.fanout",
                queue=self.queue
            )
            channel.basic_consume(queue=self.queue, on_message_callback=trace.ct_handle, auto_ack=True)
        else:

            channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": 60000})
            channel.basic_consume(queue=self.queue, on_message_callback=trace.plate_handle, auto_ack=True)

        channel.start_consuming()


    def callback(self, ch, method, properties, body):
        data = json.loads(body)
        print(data, threading.current_thread().name)
        print()


if __name__ == '__main__':

    c = Consumer()
    c.receive_msg_mq()


