pkill -f uwsgi -9
sleep 1
nohup uwsgi --socket 127.0.0.1:3031 --wsgi-file server.py --master --processes 3  > uwsgi.log &
