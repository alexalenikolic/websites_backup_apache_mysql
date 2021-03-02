import mysql.connector
import os
import subprocess
import datetime
import tarfile


def backup_sites(out_dir):
    sites_path = get_apache_sites()
    for path in sites_path:
        backup_file = path.lstrip('/').replace('/', '.',)
        with tarfile.open(out_dir+'/sites/'+backup_file+today_date()+'.tar.gz', "w:gz") as gzip:
            gzip.add(path)
            gzip.close()


def get_databases_list(mysql_credentials):
    db = mysql.connector.connect(**mysql_credentials)
    cursor = db.cursor(dictionary=True)
    query = ("show databases")
    cursor.execute(query)
    return cursor.fetchall()


def mkdir(*path):
    dir_path = '/'.join(p for p in path)+'/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def today_date():
    return datetime.datetime.today().strftime('%Y-%m-%d-%H.%M.%S')


def mysqldump(**kwargs):
    devnull = open(os.devnull, 'w')
    command = '/usr/bin/mysqldump -u {user} -p{password} {db_name} | /bin/bzip2 --best > {output}.sql.bz2'.\
        format(**kwargs)
    subprocess.call([command], shell=True, stdout=devnull, stderr=devnull)


def time_to_seconds(days=0):
    return round(datetime.datetime.timestamp(datetime.datetime.today()))
    #return round(datetime.datetime.timestamp(datetime.datetime.today()+datetime.timedelta(days=days)))

def add_days(days):
    return 60 * 60 * 24 * days

def cleanup(path, days=1):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = '/'.join([root, file])
            file_mtime = round(os.stat(file_path).st_mtime) + add_days(days) 
            if file_mtime < time_to_seconds():
                os.remove(file_path)


def open_file(file):
    with open(file, 'r') as f:
        return f.read()


def get_apache_sites():
    sites_abs_path = []
    for root, dirs, files in os.walk('/etc/apache2/sites-enabled/'):
        for file in files:
            open_file = open(root+file, 'r')
            lines = open_file.readlines()
            document_root = []
            document_root_array = []
            for line in lines:
                if line.find('DocumentRoot') > -1:
                    nospace_line = line.strip()
                    var_start = nospace_line.find('${')
                    var_end = nospace_line.find('}')+1
                    if var_start > 0:
                        document_root_array.append(nospace_line.split(' '))
                        document_root_array.append(nospace_line[var_start:var_end])
                    else:
                        document_root.append(nospace_line.split(' ')[1])
            if bool(document_root_array):
                path_var = [x[1] if isinstance(x, list) else x for x in document_root_array]
                if len(path_var) > 1:
                    for line in lines:
                        char_start = line.find('Define')
                        if char_start > -1:
                            var_dir = line.strip().split()[2]
                            output_dir = path_var[0].replace('$', '').format(wplocaldir=var_dir)
                            for i in range(len(document_root_array)):
                                if isinstance(document_root_array[i], list):
                                    document_root = output_dir
                                    #print(document_root)
                                break
                            break
            sites_abs_path.append(document_root)
    return [p[0] if isinstance(p, list) else p for p in sites_abs_path]
