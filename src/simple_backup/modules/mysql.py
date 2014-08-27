__author__ = 'am6puk'
import MySQLdb
import ConfigParser


class Model(object):
    db = None
    cursor = None
    name = 'simple_backup.conf'
    conf_path = '/etc/simple_backup/'
    config = ConfigParser.ConfigParser()
    config.read(conf_path+name)
    host = config.get('mysql', 'MYSQL_HOST')
    user = config.get('mysql', 'MYSQL_USER')
    password = config.get('mysql', 'MYSQL_PASS')

    def __init__(self):
        self.db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()



class Get_base(Model):
    def list_bases(self, exclude):
        sql = r"show databases"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        list = []
        for i in data:
            if not i[0] in exclude:
                list.append(i[0])
        return list

    def table_list(self, database):
        sql1 = r"use `{0}`".format(database)
        sql2 = r"SHOW TABLES"
        self.cursor.execute(sql1)
        self.cursor.execute(sql2)
        data = self.cursor.fetchall()
        list = []
        for i in data:
            list.append(i[0])
        return list