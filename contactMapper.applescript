on run argv
	set targetID to item 1 of argv
	
	tell application "Contacts"
		set everyone to people
		repeat with contact in everyone
			if item 2 of argv is "phone" then
				set handleList to value of phone of contact
			else -- item 2 of argv is "email"
				set handleList to value of email of contact
			end if
			set handleListLength to length of handleList
			if handleListLength > 0 then
				repeat with handleIndex from 1 to handleListLength
					if item 2 of argv is "phone" then
						set unformattedHandle to item handleIndex of handleList
						--log unformattedHandle
						set formattedHandle to my cleanString(unformattedHandle, {" ", "-", ")", "(", "."})
						--want subset matches for phones (e.g. 23456789 is in +123456789)
						if formattedHandle is in targetID then
							return name of contact
						end if
					else --item 2 of arv is "email" 
						set formattedHandle to item handleIndex of handleList
						--want exact matches for emails
						if formattedHandle is targetID then
							return name of contact
						end if
					end if
				end repeat
			end if
		end repeat
		return "None"
	end tell
	
end run

--https://discussions.apple.com/thread/5505200
on cleanString(str, chars)
	set tid to AppleScript's text item delimiters
	repeat with c in chars
		set AppleScript's text item delimiters to {c}
		set chunks to text items of str
		set AppleScript's text item delimiters to ""
		set str to chunks as Unicode text
	end repeat
	set AppleScript's text item delimiters to tid
	return str
end cleanString




