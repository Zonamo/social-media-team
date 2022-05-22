import os
import json
import sys
from datetime import datetime, timedelta
import time

print(f'cron start: {datetime.now()}')
def cronjob_unix_stamp():
    now = datetime.utcnow()
    now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f')
    now = now.replace(microsecond=0)
    unix_now = time.mktime(now.timetuple())
    f = open(os.path.join(sys.path[0], "cronjob_unix_stamp.txt"), "w")
    f.write(str(unix_now))
    f.close()
    return
cronjob_unix_stamp()

from initialise import prepare
from count_hashtags import update_data_hashtags
from count_mentions import update_data_mentions
from aggregate import aggregate


def get_unix_stamp():
    with open(os.path.join(sys.path[0], 'unix_stamp.txt'), 'r') as file:
        string = file.read()
        unix_stamp = int(json.loads(string))
    return unix_stamp

def update_unix_stamp(unix_stamp, period):
    with open(os.path.join(sys.path[0], 'unix_stamp.txt'), 'r') as file:
        string = file.read()
        unix_stamp = int(json.loads(string))
    unix_stamp += period * 60
    unix_stamp = int(format(unix_stamp, '.0f'))
    f = open(os.path.join(sys.path[0], "unix_stamp.txt"), "w")
    f.write(str(unix_stamp))
    f.close()
    return 

def time_package(unix_stamp, period):
    now = datetime.utcfromtimestamp(unix_stamp).strftime('%Y-%m-%d %H:%M:%S.%f')
    now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f') - timedelta(seconds=10)
    now = now.replace(microsecond=0)
    ago = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S') - timedelta(minutes=period)
    now = now.isoformat() + "Z"
    ago = ago.isoformat() + "Z"
    return now, ago

def update_count():
    with open(os.path.join(sys.path[0], 'update_count.txt'), 'r') as file:
        count = int(file.read())
        count += 1
    with open(os.path.join(sys.path[0], 'update_count.txt'), 'w') as file:
        file.write(str(count))
    return

def check_count():
    with open(os.path.join(sys.path[0], 'update_count.txt'), 'r') as file:
        count = int(file.read())
    return count

def initialise_unix_stamp():
    now = datetime.utcnow()
    now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f') - timedelta(seconds=20)
    now = now.replace(microsecond=0)
    unix_now = time.mktime(now.timetuple())
    f = open(os.path.join(sys.path[0], "unix_stamp.txt"), "w")
    f.write(str(unix_now))
    f.close()
    return

def First_time():
    with open(os.path.join(sys.path[0],"first_time.txt"), "r") as file:
        string = file.read() 
        if string == "0":
            initialise_unix_stamp()
            with open(os.path.join(sys.path[0],"first_time.txt"), "w") as file:
                file.write("1")
    return

def job(period):
    First_time()
    prepare()
    unix_stamp = get_unix_stamp()
    print(f'new unix stamp: {unix_stamp}')
    time_pack = time_package(unix_stamp, period)
    now = time_pack[0]
    ago = time_pack[1]
    update_data_hashtags(now, ago, unix_stamp)
    update_data_mentions(now, ago, unix_stamp)
    update_count()
    aggregate(period)
    update_unix_stamp(unix_stamp, period)

    return

#minutes
period = 240
job(period)