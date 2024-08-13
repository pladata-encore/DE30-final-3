# how to launch web backend server..

Set flask app secret key as environment variable.<br>
Launch redis server `sudo systemctl start redis6`.<br>
Launch web backend flask server `sudo systemctl start web-backend-server`.<br><br>
When debug, just run venv and server by 'python3 run.py'<br>


## This server uses gunicorn wsgi server with 4 sync workers.
