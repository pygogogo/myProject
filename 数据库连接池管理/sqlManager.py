import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
path = os.path.dirname(sys.path[0])
if path not in sys.path:
    sys.path.append(path)
import pymysql
from .config_helper import IniFileHelper
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB


class SQLManagers(object):

    __pool = None

    def __init__(self,dbName,type=1):  # 实例化后自动执行此函数
        self.config = IniFileHelper(curPath + '/config.ini')
        self.host = self.config.get_val('DBClientInfo_yizhuanmedia.host')
        self.port = self.config.get_val('DBClientInfo_yizhuanmedia.port')
        self.pwd = self.config.get_val('DBClientInfo_yizhuanmedia.password')
        self.user = self.config.get_val('DBClientInfo_yizhuanmedia.user')
        self.db = dbName
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        if type==1:
            self.conn = self.connect()
            self.cursor = self.conn.cursor()
        else:
            self.conn = self.connect_dict()
            self.cursor = self.conn.cursor()

    def connect(self):  # 此时进入数据库，游标也已经就绪
        if SQLManagers.__pool is None:
            POOL = PooledDB(
                #指定数据库连接驱动
                creator=pymysql,
                #连接池允许的最大连接数，0和None表示没有限制(缺省值 0 代表不限制)
                maxconnections=3,
                #初始化时，连接池至少创建的空闲连接，0表示不创建(缺省值 0 意味着开始时不创建连接)
                mincached=1,
                #连接池中空闲的最多连接数，0和None表示没有限制(缺省值 0 代表不限制连接池大小)
                maxcached=300,
                host=self.host,
                port=int(
                    self.port),
                user=self.user,
                passwd=self.pwd,
                db=self.db,
                #连接池中如果没有可用共享连接后，是否阻塞等待,True表示等等
                #False表示不等待然后报错(缺省值 0 或 False 代表返回一个错误；其他代表阻塞直到连接数减少)
                blocking=True,
                # 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用)。当达到最大数值时，连接会自动重新连接(关闭和重新打开)
                maxusage = 0,
                use_unicode=True,
                charset="utf8mb4",
                autocommit=True)

        return POOL.connection()

    def connect_dict(self):  # 此时进入数据库，游标也已经就绪
        if SQLManagers.__pool is None:
            POOL = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=300,
                host=self.host,
                port=int(
                    self.port),
                user=self.user,
                passwd=self.pwd,
                db=self.db,
                blocking=True,
                use_unicode=True,
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=True)

        return POOL.connection()

    def select_data(self, sql):
        resultTuple = None
        self.cursor.execute(sql)
        resultTuple = self.cursor.fetchall()
        return resultTuple

    def update_data(self, sql):
        resultDict = {}
        self.cursor.execute(sql)
        resultDict["rowCnt"] = self.cursor.rowcount
        return resultDict

    # 数据插入，返回主键Id
    def insert_data(self, sql):
        resultDict = {}
        self.cursor.execute(sql)
        rowId = int(self.cursor.lastrowid)
        resultDict["rowCnt"] = self.cursor.rowcount
        resultDict["rowId"] = rowId
        return resultDict

    def run(self, sql, args=None):
        self.cursor.execute(sql, args)

    # 批量插入数据, 第一个参数是sql语句， 第二个参数数据类型：元祖/列表
    def save_batch_data(self, sql, val):
        resultDict = {}
        self.cursor.executemany(sql, val)
        resultDict["rowCnt"] = self.cursor.rowcount
        return resultDict

    def insert_one(self, sql, val):
        """
        插入数据
        :param conn: 连接mysql
        :param sql: sql 语句
        :param val: 提交的数据
        :return:
        """

        self.cursor.execute(sql, val)
        self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == '__main__':
    # [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 60]
    s = SQLManagers('yizhuanmedia',2)
    sql = 'SELECT p.platename,c.apid,c.acname,c.acdes,c.acid FROM `authorcategory_media` c LEFT JOIN authorplate_media p on c.apid=p.pid WHERE c.acstate = 1 ORDER BY apid;'
    data = s.select_data(sql)
    print(data)