pgrep -f uwsgi | xargs kill -9
sleep 3
nohup uwsgi --http :9090 --wsgi-file server.py --master --processes 3 > uwsgi.log &
