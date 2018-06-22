#!/usr/bin/env python3
import socket
import time

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "chat.freenode.net" # Server
channel = "##SRM-OSC" # Channel
botnick = "PhoenixbotSRM" # Name of out bot(I guess Phoenix is a registered nick)
adminname = "SPYR4D4R" # Not actually required
exitcode = "bye " + botnick

ircsock.connect((server, 6667)) # SSL Port 6697
ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " " + botnick + "\n", "UTF-8"))
ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))

# join channel(s)
def joinchan(chan):
    ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))

# respond to server Pings.
def ping():
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

# sends messages to the target.
def sendmsg(msg, target=channel):
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

def main():
    joinchan(channel)
    while 1:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)

        if ircmsg.find("PRIVMSG") != -1:
            name = ircmsg.split('!', 1)[0][1:]
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]

            if len(name) < 17:
                if message.find('Hi ' + botnick) != -1:
                    sendmsg("Hello " + name + "!")
                if message[:5].find('.tell') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    else:
                        target = name
                        message = "Could not parse. Use .tell <target> <message>"
                    sendmsg(target + " : " + name + " says " + message)
            if name.lower() == adminname.lower() and message.rstrip() == exitcode:
                sendmsg("oh...okay. :'(")
                ircsock.send(bytes("QUIT \n", "UTF-8"))
                return
        else:
            if ircmsg.find("PING :") != -1:
                ping()

main()
