#!/bin/bash

eval $"rm /tmp/icon.icns"

id=`osascript -e "tell application \"Spotify\" to id of current track as string"`;
	
url="$(curl -sX GET https://embed.spotify.com/oembed\?url\=$id | cut -d '"' -f 46)";

eval $"curl -o /tmp/icon.icns $url";
