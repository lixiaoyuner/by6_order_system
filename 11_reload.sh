#!/bin/sh
#source /home/uwsgi/venv-python3.6-django2.2/bin/activate
cd /root/by6_order_system/
uwsgi --reload uwsgi_master.pid
