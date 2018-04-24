import sqlite3
import subprocess
import sys
from string import printable
import os.path
import requests
import json

pbSession = requests.Session()
pbSession.auth = ("Pushbullet API Key string here", "")
jsonHeader = {'Content-Type': 'application/json'}
pbSession.headers.update(jsonHeader)
pushURL = "https://api.pushbullet.com/v2/pushes"

def notePushBatch(title, body):
    previousMessageBatch = pushHistory(title)
    noteDataDictionary = {"title": title,
                          "body": previousMessageBatch + body,
                          "type": "note"}
    pbResponseObject = pbSession.post(pushURL,
                                      data = json.dumps(noteDataDictionary))

'''
pushHistory checks if the sender already has an active notification
If active notification exists for a sender, pushHistory dismisses the existing
notification and replaces it with a new notification that includes the old
notification content and the new message. 

pushHistory will check for existing notifications as far as max_interation
so if max_iteration = 4, then the program will find a sender's existing 
notification so long as there are 4 or less existing notifications from 
different sender(s) ahead of the sender's existing notification.

Dismissing a notification from 1 sender while leaving other existing 
notifications from other senders active and running pushHistory will cause
the while loop to exit early.
'''
def pushHistory(sender):
    currentLimit = 1
    max_iteration = 4 # higher is more costly, but deeper batch capability
    while currentLimit <= max_iteration:
        pbResponseObject = pbSession.get(pushURL,
                                     params = {"limit": int(currentLimit),
                                               "active": "true"})
        # print("currentLimit", currentLimit)
        messageDictLen = len(pbResponseObject.json()["pushes"])
        # print("Messages Dictionary Length", messageDictLen)
        if messageDictLen > 0:
            previousSender = pbResponseObject.json()["pushes"][-1]["title"]
            previousMessage = pbResponseObject.json()["pushes"][-1]["body"]
            previousIden = pbResponseObject.json()["pushes"][-1]["iden"]
            previousDismissed = pbResponseObject.json()["pushes"][-1]["dismissed"]
            # print("Previous Sender:", previousSender)
            # print("Message:", previousMessage)
            # print("Iden:", previousIden)
            # print("Dismissal status:", previousDismissed)
            if previousDismissed == True:
                # print("Dismissed!")
                return ""
            elif previousSender == sender:
                deletePush(previousIden)
                # print("Deleted Old Message")
                return previousMessage + "\n"
            else:
                # print("Notification Active")
                currentLimit += 1
        else: # pushes dictionary is empty 
            # print("Messages Dictionary length was 0?")
            currentLimit += 1
    return ""

def deletePush(iden):
    pbResponseObject = pbSession.delete(pushURL + "/" + iden)

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
        notePushBatch(formattedSenderList[batchIndex], batch)

def push(sender, message):
    notePushBatch(sender, removeBuddySays(sender, message))

if __name__ == '__main__':
    if int(sys.argv[1]) == 1: # e.g. python -i iMessagePush.py "1" "Name" "Hi!"
        sender = sys.argv[2]
        message = sys.argv[3]
        push(sender, message)
    else: # int(sys.argv[1]) > 1 thus indicating batch-message state
        getMostRecent(int(sys.argv[1]))