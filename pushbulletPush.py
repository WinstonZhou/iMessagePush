import sys
from pushbullet import Pushbullet

pb = Pushbullet("Pushbullet API Key string here")

def push(sender, message):
    push = pb.push_note(sender, message)

if __name__ == '__main__':
    sender = sys.argv[1]
    message = sys.argv[2]
    push(sender, message)
