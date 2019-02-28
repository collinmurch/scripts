#!/bin/bash

while true; do
	info=$(curl -s "www.flashalert.net/id/UniversityPrep" | grep "Operating as Usual.");
	if [ -z "$info" ]; then
		echo "NEW INFO!!! $info";
		osascript -e "display dialog \"NEW INFO!!!\"" &>/dev/null;
		exit 1
	else
		echo "Nothing new.";
	fi

	sleep 60
done
