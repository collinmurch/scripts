#!/bin/bash

while true; do
	info=$(curl -s "-- Website --" | grep "Operating as Usual.");
	if [ -z "$info" ]; then
		osascript -e "display dialog \"New info!\"" &>/dev/null;
		exit 1
	else
		echo "Nothing new.";
	fi

	sleep 60
done
