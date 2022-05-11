#coding: utf-8
import configupdater
import pika
import json


class Producer():
    def __init__(self):
        conf = configupdater.ConfigUpdater()
        conf.read('config.ini', encoding="utf-8")
        self.user = conf['prmq_zl']['user'].value
        self.password = conf['prmq_zl']['password'].value
        self.ip = conf['prmq_zl']['ip'].value
        self.port = int(conf['prmq_zl']['port'].value)
        self.vhost = conf['prmq_zl']['vhost'].value
        self.queue = conf['prmq_zl']['queue'].value
        # self.queue = queue

    def send_msg_mq(self, msg):
        """
        发送mq消息
        """
        credentials = pika.PlainCredentials(self.user, self.password)
        s_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.ip, port=self.port, virtual_host=self.vhost,
                                      credentials=credentials))
        channel = s_conn.channel()

        channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": 259200000})

        channel.basic_publish(exchange='',  # 为空：代表简单模式
                              routing_key=self.queue,  # 发送消息到此队列
                              body=msg,
                              properties=pika.BasicProperties(delivery_mode=2)  # 设置消息持久化，将要发送的消息的属性标记为2，表示该消息要持久化
                              )

        # channel.exchange_declare(
        #     exchange="radar.vehicle.track.display.fanout",
        #     exchange_type="fanout",
        #     arguments={"x-message-ttl": 60000}
        # )
        #
        # channel.basic_publish(exchange='radar.vehicle.track.display.fanout',  # 发送消息到交换机
        #                       routing_key="",  # 发送消息到交换机 队列为空
        #                       body=msg
        #                       )


