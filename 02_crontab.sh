#!/bin/sh
#source /home/uwsgi/venv-python3.6-django2.2/bin/activate

#Add the following line into the crontab config
#* * * * *  /home/uwsgi/by6/02_autorun_crontab.sh > /dev/null 2>&1

/root/.local/share/virtualenvs/by6_order_system-BcVATTQB/bin/python /root/by6_order_system/03_sendmail.py 
