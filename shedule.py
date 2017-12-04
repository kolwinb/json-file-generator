#!/usr/bin/python
import datetime
import time
import subprocess
import os
import signal
import psutil

now = datetime.datetime.now()
#enter shedule time
next_start = datetime.datetime(now.year,now.month,now.day+1,6,0,0)
while True:
    nown=datetime.datetime.now()
    if nown == next_start:
       #please add here to time for execute
        next_start += datetime.timedelta(days=1)
        print ("Today : ",nown.strftime('%Y-%m-%d-%H-%M-%S')+" next date",next_start.strftime('%Y-%m-%d-%H-%M-%S'))
        os.system("pkill -9 -f ApiPlayProcess.py")  
        subprocess.Popen(['python','ApiPlayProcess.py'])
        time.sleep(30)
