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

def push(sender, message):
    push = pb.push_note(sender, removeBuddySays(sender, message))

if __name__ == '__main__':
    sender = sys.argv[1]
    message = sys.argv[2]
    push(sender, message)

