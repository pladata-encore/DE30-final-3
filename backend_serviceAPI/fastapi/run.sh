#!/bin/bash

LOGFILE="/tmp/run.log"

# Function to activate the virtual environment and set PYTHONPATH
activate_env() {
  echo "$(date) - Activating virtual environment" >> $LOGFILE
  source ~/FastAPI/bin/activate
  export PYTHONPATH=/home/ec2-user/FastAPI/DE30-final/app
  echo "$(date) - Virtual environment activated and PYTHONPATH set to $PYTHONPATH" >> $LOGFILE
}

# Function to start the FastAPI server
start_server() {
  activate_env
  cd /home/ec2-user/FastAPI/DE30-final
  echo "$(date) - Starting Uvicorn server" >> $LOGFILE
  uvicorn app.main:app --host 10.11.10.180 --port 8000 --workers 4
  echo "$(date) - Uvicorn server started" >> $LOGFILE
}

# Function to stop the FastAPI server
stop_server() {
  if [ -f uvicorn.pid ]; then
    echo "$(date) - Stopping Uvicorn server with PID $(cat uvicorn.pid)" >> $LOGFILE
    kill -9 $(cat uvicorn.pid)
    rm uvicorn.pid
    echo "$(date) - Uvicorn server stopped" >> $LOGFILE
  fi
}

# Check if at least one argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 {start_server|stop_server}" >> $LOGFILE
  exit 1
fi

COMMAND=$1

case $COMMAND in
  start_server)
    start_server
    ;;
  stop_server)
    stop_server
    ;;
  *)
    echo "Usage: $0 {start_server|stop_server}" >> $LOGFILE
    exit 1
    ;;
esac
