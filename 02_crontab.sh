#!/bin/sh
#source /home/uwsgi/venv-python3.6-django2.2/bin/activate

#Add the following line into the crontab config
#* * * * *  /home/uwsgi/by6/02_autorun_crontab.sh > /dev/null 2>&1

python36 /home/uwsgi/by6/03_sendmail.py 
