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


class GetBase(Model):
    def list_bases(self, exclude):
        sql = r"show databases"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        lists = []
        for i in data:
            if not i[0] in exclude:
                lists.append(i[0])
        return lists

    def table_list(self, database):
        set_base = r"use `{0}`".format(database)
        get_tables = r"SHOW TABLES"
        self.cursor.execute(set_base)
        self.cursor.execute(get_tables)
        data = self.cursor.fetchall()
        lists = []
        for i in data:
            lists.append(i[0])
        return lists