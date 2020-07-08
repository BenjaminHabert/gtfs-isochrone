pgrep -f uwsgi | xargs kill -9
sleep 3
nohup uwsgi --socket 127.0.0.1:3031 --wsgi-file server.py --master --processes 3 > uwsgi.log &
