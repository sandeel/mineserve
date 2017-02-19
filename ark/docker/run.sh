#!/usr/bin/env bash

echo "###########################################################################"
echo "# Ark Server - " `date`
echo "# UID $UID - GID $GID"
echo "###########################################################################"
[ -p /tmp/FIFO ] && rm /tmp/FIFO
mkfifo /tmp/FIFO

export TERM=linux

function stop {
	if [ ${BACKUPONSTOP} -eq 1 ] && [ "$(ls -A server/ShooterGame/Saved/SavedArks)" ]; then
		echo "[Backup on stop]"
		arkmanager backup
	fi
	if [ ${WARNONSTOP} -eq 1 ];then 
	    arkmanager stop --warn
	else
	    arkmanager stop
	fi
	exit
}

source /home/steam/install.sh

# Change working directory to /ark to allow relative path
cd /ark

# If there is uncommented line in the file
CRONNUMBER=`grep -v "^#" /ark/crontab | wc -l`
if [ $CRONNUMBER -gt 0 ]; then
	echo "Loading crontab..."
	# We load the crontab file if it exist.
	crontab /ark/crontab
	# Cron is attached to this process
	sudo cron -f &
else
	echo "No crontab set."
fi

# Launching ark server
if [ $UPDATEONSTART -eq 0 ]; then
	arkmanager start -noautoupdate
else
	arkmanager start
fi


# Stop server in case of signal INT or TERM
echo "Waiting..."
trap stop INT
trap stop TERM

read < /tmp/FIFO &
wait
