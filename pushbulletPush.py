import os.path
from pushbullet import Pushbullet

path = os.path.dirname(os.path.realpath(__file__)) + os.sep + "messageInfo.txt"

pb = Pushbullet("Pushbullet API Key Here")

messageFile = open(path)
messageReading = messageFile.read()
messageContents = messageReading.split("::::")

push = pb.push_note(messageContents[0], messageContents[1])
