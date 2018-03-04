import sqlite3
import subprocess
import datetime
import sys
from pushbullet import Pushbullet
from string import printable

pb = Pushbullet("Pushbullet API Key string here")

# https://stackoverflow.com/questions/7147396/ (Code Citation)
def removeHidden(inputString): # removes hidden strings
    return ''.join(char for char in inputString if char in printable)

# Remove potential "{Buddy} says" prefix string 
def removeBuddySays(sender, message):
    messageList = message.split(" ")
    offendingPhrase = sender.split(" ") + ["says"]
    # print(offendingPhrase)

    # Remove offending phrase
    for i, offendingWord in enumerate(offendingPhrase):
        if removeHidden(offendingWord) == removeHidden(messageList[0]):
            # print("Removing ", messageList[0])
            messageList.pop(0)
        else: # no offending phrase
            return message
    return " ".join(messageList)

# iMessage on macOS stores timestamps with a January 1, 2001 epoch time
# which is 978307200 seconds behind the UNIX epoch time of 1/1/70
def iMessageUNIXTime(unixTime):
    return (unixTime - 978307200)

# Determines when the Macintosh last entered the S3 "sleep" ACPI power state
def lastSleepStart():
    sleepTime = subprocess.check_output("pmset -g log|grep -e ' Sleep  ' | tail -n 1", 
                                        shell = True).decode("utf-8")[:19] # 19 is the relevant portion
    # print(sleepTime)
    # Convert to iMessage chat.db datetime
    sleepTime = iMessageUNIXTime(datetime.datetime.strptime(sleepTime,
                                                            "%Y-%m-%d %H:%M:%S").timestamp())
    return sleepTime

# Determines when the Macintosh last entered the S5 "Shutdown" ACPI power state
def lastShutdown():
    shutdownTime = subprocess.check_output("syslog | grep -e 'shutdown' | tail -n 1", 
                                        shell = True).decode("utf-8").split(" ")[-2]
    # print(shutdownTime)
    shutdownTime = iMessageUNIXTime(int(shutdownTime))
    return shutdownTime

# Retrieves and pushes new iMessages based on the time the Macintosh was last
# shut down or put to sleep
def getMostRecent(startingTime):
    conn = sqlite3.connect("~/library/messages/chat.db")
    c =  conn.cursor()
    messageList = []
    senderDict = {}
    senderList = []
    senderCounter = 0
    recentIndex = (startingTime, )
    batchedMessageList = []
    for row in c.execute("SELECT handle_id, text, date/1000000000, is_sent from message where date/1000000000 > ? and is_sent < 1", recentIndex):
        messageList.append(row)
    # print(messageList)
    for message in messageList:
        t = (message[0],)
        c.execute("SELECT id FROM handle where rowid = ?", t)
        senderDict[t[0]] = c.fetchone()[0]
    # print(senderDict)
    for key in senderDict:
        senderList.append(senderDict[key])
        batchedMessageList.append("")
        for message in messageList:
            if key == message[0]:
                batchedMessageList[senderCounter] += (message[1]) + "\n"
        senderCounter += 1
    # print(senderList)
    # print(batchedMessageList)
    for batchIndex, batch in enumerate(batchedMessageList):
        push = pb.push_note(senderList[batchIndex], batch)

# Pushes a single iMessage
def push(sender, message):
    push = pb.push_note(sender, removeBuddySays(sender, message))

if __name__ == '__main__':
    if sys.argv[1] == "Shutdown":
        getMostRecent(lastShutdown())
    elif sys.argv[1] == "Sleep":
        getMostRecent(lastSleepStart())
    else: # sys.argv[1] == "Single":
        sender = sys.argv[2]
        message = sys.argv[3]
        push(sender, message)
