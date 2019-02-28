on run argv
	tell application "System Events"
		tell process "SystemUIServer"
			tell (menu bar item 1 of menu bar 1 where description is "bluetooth")
				click
				if menu item "Turn Bluetooth On" of menu 1 exists then
					tell (menu item "Turn Bluetooth On" of menu 1)
						click
					end tell
					delay 1
					click
					if menu item "Collin's Airpods" of menu 1 exists then
						tell (menu item "Collin's Airpods" of menu 1)
							click
							set menu_name to name of menu item 1 of menu 1
							if menu_name is "Connect" then
								click menu item 1 of menu 1
							end if
						end tell
					else
						key code 53
						return
					end if
				else
					if menu item "Turn Bluetooth Off" of menu 1 exists then
						tell (menu item "Turn Bluetooth Off" of menu 1)
							click
						end tell
					else
						key code 53
						return
					end if
				end if
			end tell
		end tell
	end tell
end run
