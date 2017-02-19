#!/usr/bin/env bash

# Add a template directory to store the last version of config file
[ ! -d /ark/template ] && mkdir /ark/template
# We overwrite the template file each time
cp /home/steam/arkmanager.cfg /ark/template/arkmanager.cfg
cp /home/steam/crontab /ark/template/crontab
# Creating directory tree && symbolic link
[ ! -f /ark/arkmanager.cfg ] && cp /home/steam/arkmanager.cfg /ark/arkmanager.cfg
[ ! -d /ark/log ] && mkdir /ark/log
[ ! -d /ark/backup ] && mkdir /ark/backup
[ ! -d /ark/staging ] && mkdir /ark/staging
[ ! -L /ark/Game.ini ] && ln -s server/ShooterGame/Saved/Config/LinuxServer/Game.ini Game.ini
[ ! -L /ark/GameUserSettings.ini ] && ln -s server/ShooterGame/Saved/Config/LinuxServer/GameUserSettings.ini GameUserSettings.ini
[ ! -f /ark/crontab ] && cp /ark/template/crontab /ark/crontab


if [ ! -d /ark/server  ] || [ ! -f /ark/server/arkversion ];then 
	echo "No game files found. Installing..."
	mkdir -p /ark/server/ShooterGame/Saved/SavedArks
	mkdir -p /ark/server/ShooterGame/Content/Mods
	mkdir -p /ark/server/ShooterGame/Binaries/Linux/
	touch /ark/server/ShooterGame/Binaries/Linux/ShooterGameServer
	arkmanager install
	# Create mod dir
else

	if [ ${BACKUPONSTART} -eq 1 ] && [ "$(ls -A server/ShooterGame/Saved/SavedArks/)" ]; then 
		echo "[Backup]"
		arkmanager backup
	fi
fi

arkmanager installmods

# Change working directory to /ark to allow relative path
cd /ark

