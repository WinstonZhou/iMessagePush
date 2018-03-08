# DO NOT ACCIDENTLY UPLOAD THIS TO GITHUB
# Rename as iMessagePush.py once setup complete

import sqlite3
import subprocess
import sys
from pushbullet import Pushbullet
from string import printable
import os.path

pb = Pushbullet("Pushbullet API Key string here")

def removeHidden(inputString): 
    return ''.join(char for char in inputString if char in printable)

def removeBuddySays(sender, message):
    messageList = message.split(" ")
    offendingPhrase = sender.split(" ") + ["says"]
    for i, offendingWord in enumerate(offendingPhrase):
        if removeHidden(offendingWord) == removeHidden(messageList[0]):
            messageList.pop(0)
        else: 
            return message
    return " ".join(messageList)

def iMessageUNIXTime(unixTime):
    return (unixTime - 978307200)

def getMostRecent(n):
    contactMappingPath = os.path.expanduser("~/library/Application Scripts/com.apple.iChat/contactMapper.applescript")
    conn = sqlite3.connect(os.path.expanduser("~/library/messages/chat.db"))
    c =  conn.cursor()
    messageList = []
    senderDict = {}
    senderList = []
    formattedSenderList = [] # actual sender names from Contacts application
    senderCounter = 0
    recentIndex = (n, )
    batchedMessageList = []
    for row in c.execute("select * from (select handle_id, text, rowid from message where is_sent < 1 order by rowid DESC LIMIT ?) order by rowid ASC;", recentIndex):
        messageList.append(row)
    # print("MessageList:", messageList)
    for message in messageList:
        t = (message[0],)
        c.execute("SELECT id FROM handle where rowid = ?", t)
        senderDict[t[0]] = c.fetchone()[0]
    # print("SenderDictionary:", senderDict)
    # Construct a list batchedMessageList where each element is a string
    # representing the batched messages of a single sender
    for key in senderDict:
        senderList.append(senderDict[key])
        batchedMessageList.append("")
        for message in messageList:
            if key == message[0]:
                batchedMessageList[senderCounter] += (message[1]) + "\n"
        senderCounter += 1
    for i in range(len(batchedMessageList)):
        batchedMessageList[i] = batchedMessageList[i][:-1] # remove last newline character
    # print("SenderList:", senderList)
    for senderIndex, sender in enumerate(senderList):
        if "@" in sender: #iMessage ID is an email address
            formattedName = subprocess.check_output("osascript '%s' '%s' 'email'" % (contactMappingPath, sender), shell = True).decode("utf-8")
        else: #iMessage ID is a phone number
            formattedName =subprocess.check_output("osascript '%s' '%s' 'phone'" % (contactMappingPath, sender), shell = True).decode("utf-8")
        if formattedName != "None\n": # matched iMessage ID with a contact's name successfully
            formattedSenderList.append(formattedName)
        else: # iMessage ID not listed in Contacts application
            formattedSenderList.append(sender)
        # remove trailing newlines from formatted name
        formattedSenderList[senderIndex] = formattedSenderList[senderIndex].strip('\n') 
    # print("Formatted SenderList:", formattedSenderList)
    # print("BatchedMessageList:", batchedMessageList)
    for batchIndex, batch in enumerate(batchedMessageList):
        push = pb.push_note(formattedSenderList[batchIndex], batch)

def push(sender, message):
    push = pb.push_note(sender, removeBuddySays(sender, message))

if __name__ == '__main__':
    if int(sys.argv[1]) == 1:
        sender = sys.argv[2]
        message = sys.argv[3]
        push(sender, message)
    else: # int(sys.argv[1]) > 1 thus indicating batch-message state
        getMostRecent(int(sys.argv[1]))
        
        
 
