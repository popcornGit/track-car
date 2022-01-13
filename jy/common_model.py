#coding；utf-8
import time
from mysqldb import MySQLdb
db = MySQLdb()


class CommonModel():

    @classmethod
    def submit_event(cls, data):
        sql = """INSERT INTO target_track(
                    `data`,
                    `create_time`
                ) VALUES(
                    '{}',
                    {}
                )     
            """.format(data, int(time.time()))

        db.insert(sql)






