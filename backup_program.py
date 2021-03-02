#!/usr/bin/python3
import __functions as f

days_old = 7  # delete files that are more than <days> old

db_data = dict({"user": "root", "password": "m4t1j4Nikolic",
                          "host": "localhost","database":"mysql"})
skip_db = ['information_schema', 'mysql', 'performance_schema']
output_directory = "/opt/backup"

print("@", f.today_date(), "Starting backup")


databases = f.get_databases_list(db_data)
today_date = f.today_date()

print('DUMPING DATABASES')
for db in databases:
    db_name = db['Database']
    f.mkdir(output_directory+'/databases/')
    f.mkdir(output_directory+'/sites/')
    #path = f.mkdir(output_directory, db_name)
    if db_name in skip_db:
        continue
    file_name = output_directory+'/databases/'+db_name+'.'+today_date
#    f.mysqldump(user=db_data['user'], password=db_data['password'], db_name=db_name, output=file_name)

print("COPYING SITES TO BACKUP PATH")
#f.backup_sites(output_directory)

print("CLEANING OLD FILES")
f.cleanup(output_directory, days_old)
print("@", f.today_date(), "Finishing backup")
