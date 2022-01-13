#coding:utf-8
import pymysql
import logging


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
        self.port = 23308
        self.user = "root"
        self.password = "XE1gPm2QfqxbERMp"
        self.database = "event_db"
        self.charset = charset
        try:
            self.connect()
        except Exception as e:
            logging.getLogger("error.log").error(e)

    def connect(self):
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database)
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

