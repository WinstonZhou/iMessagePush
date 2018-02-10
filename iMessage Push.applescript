using terms from application "Messages"
	
	on message received theMessage from theBuddy for theChat with theMessageText
		set senderName to (get name of theBuddy)
		set messageContents to theMessageText
		set messageBlock to senderName & "::::" & messageContents
		set messageInfoPath to "/Users/winstonzhou/Library/Application Scripts/com.apple.iChat/messageInfo.txt"
		set eof messageInfoPath to 0
		set myFile to open for access (messageInfoPath) with write permission
		write messageBlock to myFile
		close access myFile
		do shell script "python -i '/Users/winstonzhou/Library/Application Scripts/com.apple.iChat/pushbulletPush.py'"
	end message received
	
	# The following are unused but need to be defined to avoid an error
	
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

