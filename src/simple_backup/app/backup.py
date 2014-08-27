import os
import datetime
import shutil
import subprocess
import ConfigParser
try:
    import MySQLdb
except ImportError:
    pipinstall = subprocess.Popen("apt-get install python-mysqldb -y", shell=True)
    pipinstall.wait()
    import MySQLdb
from simple_backup.modules.mysql import GetBase
from simple_backup.modules.mail import send

name = 'simple_backup.conf'
conf_path = '/etc/simple_backup/'
config = ConfigParser.ConfigParser()
config.read(conf_path+name)
host = config.get('mysql', 'MYSQL_HOST')
user = config.get('mysql', 'MYSQL_USER')
password = config.get('mysql', 'MYSQL_PASS')
BACKUP_DIR = config.get('mysql', 'BACKUP_DIR')
DUMP_PERF = config.get('mysql', 'DUMP_PERF')
HOTCOPY_PREF = config.get('mysql', 'HOTCOPY_PREF')



def backup_db(dir_pref, num_dir, type):
    dt = datetime.datetime.now()
    date_now = dt.strftime('%Y-%m-%d_%H%M')
    backup_dir = None
    exclude = None
    if type == 'dump':
        backup_dir = BACKUP_DIR+DUMP_PERF
        exclude = config.get('dump', 'EXCLUDE_LIST')

    elif type == 'hotcopy':
        backup_dir = BACKUP_DIR+HOTCOPY_PREF
        exclude = config.get('hotcopy', 'EXCLUDE_LIST')
    else:
        print 'Wrong type of backup'

    list = []

    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    list_dir_all = os.listdir(backup_dir)
    for dir in list_dir_all:
        if dir.startswith(dir_pref):
            list.append(dir)
    #print list
    count_dir = len(list)
    age = []
    dic = {}
    for x in list:
        age.append(os.path.getmtime(backup_dir+x))
        dic[os.path.getmtime(backup_dir+x)] = x
        age.sort()
        dic[age[0]]

    if count_dir > num_dir:
        shutil.rmtree(backup_dir+dic[age[0]])

    try:
        bases = GetBase()
        sorted_list = bases.list_bases(exclude)
        for base in sorted_list:
            print 'Now backuping database {0}'.format(base)
            if not os.path.exists(backup_dir):
                os.mkdir(backup_dir)
            if not os.path.exists(backup_dir+dir_pref+date_now):
                os.mkdir(backup_dir+dir_pref+date_now)
            cmd = None
            if type == 'dump':
                cmd = r'/usr/bin/mysqldump -u {0} -p{1} {2} | gzip >> "{3}"'.format(user, password, base, backup_dir+dir_pref+date_now+'/'+base+'.sql.gz')
            elif type == 'hotcopy':
                cmd = r'/usr/bin/mysqlhotcopy -u {0} -p {1} {2} {3} >> /dev/null'.format(user, password, base, backup_dir+dir_pref+date_now)
            else:
                print 'Wrong type of backup'

            run = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            run.wait()
            out = run.communicate()
            print out
    except MySQLdb.OperationalError, err:
        error = unicode(err)
        print error
        #send(Config.MESSAGE["1"], error)

def backup_db_per_table(dir_pref, num_dir, type):
    dt = datetime.datetime.now()
    date_now = dt.strftime('%Y-%m-%d_%H%M')
    backup_dir = None
    exclude = None
    if type == 'dump':
        backup_dir = BACKUP_DIR+DUMP_PERF
        exclude = config.get('dump', 'EXCLUDE_LIST')
        #table_exclude = config.get('table_exclude', 'EXCLUDE_LIST')
    elif type == 'hotcopy':
        backup_dir = BACKUP_DIR+HOTCOPY_PREF
        exclude = config.get('hotcopy', 'EXCLUDE_LIST')
        #table_exclude = config.get('table_exclude', 'EXCLUDE_LIST')
    else:
        print 'Wrong type of backup'

    list = []

    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    list_dir_all = os.listdir(backup_dir)
    for dir in list_dir_all:
        if dir.startswith(dir_pref):
            list.append(dir)
    #print list
    count_dir = len(list)
    age = []
    dic = {}
    for x in list:
        age.append(os.path.getmtime(backup_dir+x))
        dic[os.path.getmtime(backup_dir+x)] = x
        age.sort()
        dic[age[0]]

    if count_dir > num_dir:
        shutil.rmtree(backup_dir+dic[age[0]])

    try:
        bases = GetBase()
        sorted_list = bases.list_bases(exclude)
        table_exclude = config.get('table_exclude', 'EXCLUDE_LIST')
        for base in sorted_list:
            sorted_table = bases.table_list(base)
            #print 'Now backuping database {0}'.format(base)
            if not os.path.exists(backup_dir):
                os.mkdir(backup_dir)
            if not os.path.exists(backup_dir+dir_pref+date_now):
                os.mkdir(backup_dir+dir_pref+date_now)
            if not os.path.exists(backup_dir+dir_pref+date_now+'/'+base):
                os.mkdir(backup_dir+dir_pref+date_now+'/'+base)
            cmd = None
            for table in sorted_table:
                print 'Now backuping database {0} Table {1}'.format(base, table)
                if type == 'dump':
                    cmd = r'/usr/bin/mysqldump -u {0} -p{1} {2} {3} | gzip >> "{4}"'.format(user, password, base, table, backup_dir+dir_pref+date_now+'/'+base+'/'+table+'.sql.gz')
                elif type == 'hotcopy':
                    cmd = r'/usr/bin/mysqlhotcopy -u {0} -p {1} {2} {3} >> /dev/null'.format(user, password, base, backup_dir+dir_pref+date_now)
                else:
                    print 'Wrong type of backup'

                run = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                run.wait()
                out = run.communicate()
                print out
    except MySQLdb.OperationalError, err:
        error = unicode(err)
        print error
        #send(Config.MESSAGE["1"], error)


