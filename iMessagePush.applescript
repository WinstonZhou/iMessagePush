using terms from application "Messages"
	on unixCurrentDate(datetime) -- returns unix time as a date object
		set command to "date -j -f '%A, %B %e, %Y at %I:%M:%S %p' '" & datetime & "'"
		set command to command & " +%s"
		
		set theUnixDate to do shell script command
		return theUnixDate
	end unixCurrentDate
	
	on unixWakeDate(datetime) --returns wake time which can be matched to the sqldb
		set command to "date -j -f '%Y-%m-%e %H:%M:%S' '" & datetime & "'"
		set command to command & " +%s"
		
		set theUnixDate to do shell script command
		return theUnixDate
	end unixWakeDate
	
	-- https://www.macosxautomation.com/applescript/sbrt/sbrt-02.html (Code citation)
	on number_to_string(this_number)
		set this_number to this_number as string
		if this_number contains "E+" then
			set x to the offset of "." in this_number
			set y to the offset of "+" in this_number
			set z to the offset of "E" in this_number
			set the decimal_adjust to characters (y - (length of this_number)) thru Â
				-1 of this_number as string as number
			if x is not 0 then
				set the first_part to characters 1 thru (x - 1) of this_number as string
			else
				set the first_part to ""
			end if
			set the second_part to characters (x + 1) thru (z - 1) of this_number as string
			set the converted_number to the first_part
			repeat with i from 1 to the decimal_adjust
				try
					set the converted_number to Â
						the converted_number & character i of the second_part
				on error
					set the converted_number to the converted_number & "0"
				end try
			end repeat
			return the converted_number
		else
			return this_number
		end if
	end number_to_string
	
	on message received theMessage from theBuddy for theChat with theMessageText
		try -- immediately remove any existing sleep cycling
			do shell script "crontab -r" password "Insert administrative password here" with administrator privileges
		on error
			log "Cron is not empty"
		end try
		set senderName to (get name of theBuddy)
		set messageContents to theMessageText

		-- Retrieve timestamp of when Macintosh was last powered on from S5 shutdown
		set lastBoot to do shell script "pmset -g log|grep -e 'Start'| tail -n 1"
		-- '' was last woken from S3 sleep
		set lastWake to do shell script "pmset -g log|grep -e ' Sleep  ' -e ' Wake  '| tail -n 1"
		set wakeDate to text 1 thru 19 of lastWake
		set bootDate to text 1 thru 19 of lastBoot
		log {"Seconds since last wake", unixCurrentDate(current date) - unixWakeDate(wakeDate)}
		log {"Seconds since last boot", unixCurrentDate(current date) - unixWakeDate(bootDate)}

		(* Compute the number of seconds since the Macintosh was last powered on
		and woken from sleep *)
		set secondsSinceBoot to unixCurrentDate(current date) - unixWakeDate(bootDate)
		set secondsSinceWake to unixCurrentDate(current date) - unixWakeDate(wakeDate)
		if secondsSinceWake < 60 then -- Batch State: From wake
			try
				(* Prevent parallel execution of iMessagePush.py by creating
				a directory called ~/lock that acts as a semaphore. Only one
				instance of this applescript will manage to create the lock
				directory, which once created will lock out all other instances
				of this applescript that were running in parallel.	*)
				set lockStatus to do shell script "mkdir ~/lock"
				do shell script "/usr/local/bin/python3 \"~/Library/Application Scripts/com.apple.iChat/iMessagePush.py\" \"Sleep\" && rm -r ~/lock"

				(* Prevent the Macintosh server from entering its sleep state
				for at least another 30 minutes (1800 seconds) if this 
				applescript runs. *)
				set newSleepTime to number_to_string(unixCurrentDate(current date) + 1800) 
				set cronSleepHour to do shell script "date -r " & newSleepTime & " +%-H"
				set cronSleepMinute to do shell script "date -r " & newSleepTime & " +%-M"
				-- Sleep cycle command
				do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * crontab -r && (crontab -l; echo \"*/2 0-1,8-23 * * * sudo pmset relative wake 1800 && sudo pmset sleepnow \") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
				-- Shutdown cycle command
				do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * (crontab -l; echo \"*/5 2-6 * * * sudo /sbin/shutdown -h now\") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
			on error
				log "Lock Exists"
			end try
		else
			if secondsSinceBoot < 90 then --Batch State: From shutdown
				try
					set lockStatus to do shell script "mkdir ~/lock"
					do shell script "/usr/local/bin/python3 \"~/Library/Application Scripts/com.apple.iChat/iMessagePush.py\" \"Shutdown\" && rm -r /users/winstonzhou/lock"
					set newSleepTime to number_to_string(unixCurrentDate(current date) + 1800) 
					set cronSleepHour to do shell script "date -r " & newSleepTime & " +%-H"
					set cronSleepMinute to do shell script "date -r " & newSleepTime & " +%-M"
					do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * crontab -r && (crontab -l; echo \"*/2 0-1,8-23 * * * sudo pmset relative wake 1800 && sudo pmset sleepnow \") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
					do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * (crontab -l; echo \"*/5 2-6 * * * sudo /sbin/shutdown -h now\") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
				on error
					log "Lock Exists"
				end try
			else -- Single Message State: > 60/90 seconds since boot/startup
				do shell script "/usr/local/bin/python3 \"~/Library/Application Scripts/com.apple.iChat/iMessagePush.py\" \"Single\" " & quoted form of senderName & " " & quoted form of messageContents
				log "SINGLE-MESSAGE STATE: BOOT/WAKE > 60/90"
				set newSleepTime to number_to_string(unixCurrentDate(current date) + 1800) 
				set cronSleepHour to do shell script "date -r " & newSleepTime & " +%-H"
				set cronSleepMinute to do shell script "date -r " & newSleepTime & " +%-M"
				do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * crontab -r && (crontab -l; echo \"*/2 0-1,8-23 * * * sudo pmset relative wake 1800 && sudo pmset sleepnow \") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
				do shell script "(crontab -l; echo '" & cronSleepMinute & " " & cronSleepHour & " * * * (crontab -l; echo \"*/5 2-6 * * * sudo /sbin/shutdown -h now\") | crontab -') | crontab -" password "Insert administrative password here" with administrator privileges
			end if
		end if
		
	end message received
	
	(* https://discussions.apple.com/thread/6476545 (Code citation)
	Empty handlers below *)
	
	on received text invitation theText from theBuddy for theChat
		
	end received text invitation
	
	on received audio invitation theText from theBuddy for theChat
		
	end received audio invitation
	
	on received video invitation theText from theBuddy for theChat
		
	end received video invitation
	
	on received file transfer invitation theFileTransfer
		
	end received file transfer invitation
	
	on buddy authorization requested theRequest
		
	end buddy authorization requested
	
	on message sent theMessage for theChat
		
	end message sent
	
	on chat room message received theMessage from theBuddy for theChat
		
	end chat room message received
	
	on active chat message received theMessage
		
	end active chat message received
	
	on addressed chat room message received theMessage from theBuddy for theChat
		
	end addressed chat room message received
	
	on addressed message received theMessage from theBuddy for theChat
		
	end addressed message received
	
	on av chat started
		
	end av chat started
	
	on av chat ended
		
	end av chat ended
	
	on login finished for theService
		
	end login finished
	
	on logout finished for theService
		
	end logout finished
	
	on buddy became unavailable theBuddy
		
	end buddy became unavailable
	
	on completed file transfer
		
	end completed file transfer
end using terms from

