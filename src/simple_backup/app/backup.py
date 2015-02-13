import os
import datetime
import shutil
import subprocess
import ConfigParser
import glob
import time
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
section = 'mysql'
config = ConfigParser.ConfigParser()
config.read(conf_path+name)
host = config.get(section, 'MYSQL_HOST')
user = config.get(section, 'MYSQL_USER')
password = config.get(section, 'MYSQL_PASS')
BACKUP_DIR = config.get(section, 'BACKUP_DIR')
DUMP_PERF = config.get(section, 'DUMP_PERF')
HOTCOPY_PREF = config.get(section, 'HOTCOPY_PREF')


def sort_dir(pref):

    root = BACKUP_DIR+DUMP_PERF+pref+'*'

    date_file_list = []
    for folder in glob.glob(root):
        stats = os.stat(folder)
        lastmod_date = time.localtime(stats[8])
        date_file_tuple = lastmod_date, folder
        date_file_list.append(date_file_tuple)

    date_file_list.sort()
    date_file_list.reverse()  # newest mod date now first
    full_clear_list = []
    for folder1 in date_file_list:
        full_clear_list.append(folder1[1])
    return full_clear_list


def delete_old_dirs(full_clear_list, num_dir):

    removal_list = []
    for old_dir in full_clear_list:
            if old_dir not in full_clear_list[0:int(num_dir)]:
                    removal_list.append(old_dir)
    print removal_list
    if removal_list:
        for rm_dir in removal_list:
            shutil.rmtree(rm_dir)
    else:
        pass


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


    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    dir_sorted_list = sort_dir(dir_pref)
    delete_old_dirs(dir_sorted_list, num_dir)

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
                f = open(backup_dir+dir_pref+date_now+"/"+base+".sql.gz", "wb")
                cmd = ["/usr/bin/mysqldump", "-u"+user, "-p"+password, "--single-transaction", "--max_allowed_packet=1G", base]
                run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                run2 = subprocess.Popen('gzip', stdin=run.stdout, stdout=f)
                run2.wait()
                run.wait()
                f.close()
            elif type == 'hotcopy':
                cmd = ["/usr/bin/mysqlhotcopy", "-u"+user, "-p"+password, base, ">", "/dev/null", backup_dir+dir_pref+date_now]
                run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                while True:
                    line = run.stdout.readline()
                    if line != '':
                        print line
                    else:
                        break
            else:
                print 'Wrong type of backup'

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


    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    dir_sorted_list = sort_dir(dir_pref)
    delete_old_dirs(dir_sorted_list, num_dir)

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

            for table in sorted_table:

                print 'Now backuping database {0} Table {1}'.format(base, table)
                if type == 'dump':
                    f = open(backup_dir+dir_pref+date_now+"/"+base+"/"+table+".sql.gz", "wb")
                    cmd = ["/usr/bin/mysqldump", "-u"+user, "-p"+password, "--single-transaction", "--max_allowed_packet=1G", base, table]
                    run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    run2 = subprocess.Popen('gzip', stdin=run.stdout, stdout=f)
                    run2.wait()
                    run.wait()
                    f.close()
                elif type == 'hotcopy':
                    cmd = ["/usr/bin/mysqlhotcopy", "-u"+user, "-p"+password, base, backup_dir+dir_pref+date_now]
                    run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    while True:
                        line = run.stdout.readline()
                        if line != '':
                            return line
                        else:
                            break
                else:
                    print 'Wrong type of backup'

    except MySQLdb.OperationalError, err:
        error = unicode(err)
        print error
        #send(Config.MESSAGE["1"], error)


