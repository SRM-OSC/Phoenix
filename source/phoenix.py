#!/usr/bin/env python3.6
import sys
import socket
import ssl
import hashlib
import getpass
import traceback
import time
import hidden # hidden.py contains md5 password

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# alternate ciphers ECDHE-RSA-AES256-GCM-SHA384
ircsock = ssl.wrap_socket(
    ircsock, ssl_version=ssl.PROTOCOL_TLSv1_2, ciphers="DHE-RSA-AES256-GCM-SHA384")
server = "chat.freenode.net"  # Server
channel = "##SRM-OSC"  # Channel
botnick = "PhoenixSRM"
adminname = ["SPYR4D4R", "toxicmender"]  # Admins that can shutdown the bot
greetings = ["hi", "hello", "yo", "hey", "hiya", "g'day"]
valedictions = ["bye", "goodbye", "gtfo", "ciao"]

# Get the bot password from user, only admins know this password
# Password is required to verify the botnick
md5_pass = ""
password = ""
attempt = 0
while attempt < 3 and md5_pass != hidden.md5Pass:
    try:
        password = getpass.getpass(
            f"\n Enter Bot Password [Attempt: {attempt + 1}/3]: ")
        md5_pass = str(hashlib.md5(password.encode("utf-8")).hexdigest())
        attempt += 1
    except:
        print("\n Failed to get correct password. Exiting...")
        sys.exit(0)
if md5_pass == hidden.md5Pass:
    print("\n Password verified. Connecting to Freenode IRC")
else:
    print("\n Incorrect password. Exiting...")
    sys.exit(0)

# Start connection to Freenode IRC
ircsock.connect((server, 6697))  # SSL Port 6697
ircsock.send(bytes(f"USER {botnick} {botnick} {botnick} {botnick}\n", "UTF-8"))
ircsock.send(bytes(f"NICK {botnick}\n", "UTF-8"))
ircsock.send(bytes(f"NickServ IDENTIFY {password}\n", "UTF-8"))

# join channel(s)
"""
joins the channel by name on IRC

@param chan: IRC channel name
"""
def joinchan(chan):
    ircsock.send(bytes(f"JOIN {chan}\n", "UTF-8"))

# respond to server Pings.
"""
respond to connected IRC server ping
"""
def ping():
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

# sends messages to the target.
"""
sends a message string to intended target over IRC

@param msg: message string
@param target: recipient of the message string, can be either channel or a user on IRC. default is channel
"""
def sendmsg(msg, target=channel):
    print(f"PhoenixSRM: PRIVMSG {target} :{msg}")
    ircsock.send(bytes(f"PRIVMSG {target} :{msg}\n", "UTF-8"))

# sends help info as a private message to the user
"""
displays a short IRC commands cheatsheet

@param target: IRC user nick of the asker
@param topic: IRC command related query, such as nickname management. Default is all
"""
def help(target, topic="all"):

    # recursive function to print messages in intended form
    def nester(messagelist, level=1, delay=0):
        for each_message in messagelist:
            if isinstance(each_message, list):
                nester(each_message, level+1, delay)
            else:
                each_message = "\t"*level + each_message
                time.sleep(delay)
                sendmsg(each_message, target)

    # syntax flag is for wrong syntax
    syntax = ["Wrong Syntax",
              ["-> Use .help all or .help (For everything)", "-> Use .help basics (For Basic IRC Commands)", "-> Use .help nick (For Nick Management)"]]

    # basic flag for basic commands
    basics = ["## The Basics",
              ["/join #channel", ["+ Joins the specified channel."]],
              ["/part #channel", ["+ Leaves the specified channel."]],
              ["/quit [message]",
               ["+ Disconnects from current server with optional leaving message."]],
              ["/server hostname", ["+ Connects to the specified server."]],
              ["/sslserver hostname", ["+ Connects to the specified server over ssl."]],
              ["/list", ["+ Lists all the channels on the current network."]],
              ["/nick nickname", ["+ Changes your nick."]],
              ["/names #channel", ["+ Shows the nicks of all users on #channel."]],
              ["/msg nickname message", ["+ Sends a private message to a user."]],
              ["/query nickname message",
               ["+ Sends a private message to a user and opens a private chat window."]],
              ["/me action", ["+ Prints 'yourname action'."]],
              ["/notice nickname message", ["+ Sends a notice to the specified user.",
                                            "+ Like /msg, but usually with sound."]],
              ["/whois nickname", ["+ Shows information about the specified user.",
                                   "+ This action is not visible to the specified user."]],
              ["/whowas nickname", ["+ Shows information about a user who has quit."]],
              ["/ping nickname", ["+ Pings the specified user.", "+ This action is visible to the specified user."]]]

    nick = ["## Nick Management",
            ["/nickserv register password [email]", ["+ Registers your current nick with NickServ,",
                                                     "+ With the chosen password and binds it to an email address."]],
            ["/nickserv identify password", ["+ Identifies your nick to NickServ using the password you set.",
                                             "+ If you have a nick that's been registered."]],
            ["/nickserv recover nickname password",
             ["+ Kills(forcibly disconnects) someone who has your registered nick."]],
            ["/nickserv ghost nickname password",
             ["+ Terminates a 'ghost' IRC session that's using your nickname."]],
            ["/nickserv set password yournewpassword", ["+ Changes your password."]]]

    if topic == "all":
        messagelist = basics + nick
        nester(messagelist, delay=1)  # delay tested at 1 s
    elif topic == "basics":
        nester(basics, delay=1)  # delay tested at 1 s
    elif topic == "nick":
        nester(nick, delay=0.5)  # delay tested at 0.5 s
    else:
        nester(syntax)

# .tell function
"""
sends a private message (not be confused with direct message) on the channel to an IRC username

@param name: IRC user nick of the sender
@param t_message: IRC target <user_nick | channel>
"""
def tell(name, t_message="invalid"):
    if t_message.find(' ') != -1:
        message = t_message.split(' ', 1)[1]
        target = t_message.split(' ', 1)[0]
        sendmsg(f"{target} : {name} says {message}")
    else:
        message = "Could not parse. Use .tell <target> <message>"
        sendmsg(message)

# .banner function
"""
displays a welcome banner on joining of the channel by a user & title banner of the botnick. These are sent as burst message.

@param name: IRC user nick of the joining member or the user nick of asker
@param b_type: banner type <welcome | 0 | 1 | 2 |  >
"""
def banner(name, b_type="welcome"):
    import json
    import random
    with open("ascii.json", 'r', encoding="utf-8") as f:
        banners = json.load(f)
        if b_type == "welcome":
            message = banners["welcome"]
            h = ["Bot functions", "\t.help <all | basic | nick>", "\t.tell <usernick> <message>", "\t.banner <welcome |   | 0 | 1 | 2>"]
            message += h
        elif b_type in [str(r) for r in range(3)]:
            message = banners["banner"][int(b_type)]
        else:
            message = banners["banner"][random.randrange(3)]
        for line in message:
            sendmsg(line, name)


# Dictionary storing keyword as key & function object as value
plugins = {".help": help, ".tell": tell, ".banner": banner}


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
                if message.find(' ') != -1:
                    # check for greetings
                    if message.split(' ', 1)[0].lower() in greetings and message.split(' ', 1)[1].rstrip() == botnick:
                        sendmsg(message.split(' ', 1)[0] + " " + name + "!")
                    # check for valediction from an admin
                    elif name in adminname and message.split(' ', 1)[0].lower() in valedictions and message.split(' ', 1)[1].rstrip() == botnick:
                        sendmsg("oh...okay. :'('")
                        ircsock.send(bytes("QUIT \n", "UTF-8"))
                        sys.exit(0)
                    # check for a valid command
                    elif message.split(' ', 1)[0] in plugins.keys():
                        arguments = message.split(' ', 1)[1].rstrip()
                        plugins[message.split(' ', 1)[0]](name, arguments)
                elif message.rstrip() in plugins.keys():
                    plugins[message.rstrip()](name)
        elif ircmsg.find("JOIN") != -1 and ircmsg.find(botnick) == -1:
            name = ircmsg.split('!', 1)[0][1:]
            #message = ircmsg.split(channel, 1)[1].split(':', 1)[1]
            if name.lower() != "chanserv" and name.lower() != botnick:
                plugins[".banner"](name, "welcome")
        else:
            if ircmsg.find("PING :") != -1:
                ping()


try:
    main()
except KeyboardInterrupt:
    sendmsg("oops my computer went down... *_*")
except Exception:
    sendmsg("*_* admins please check... something's wrong")
    print("\n> START OF TRACEBACK\n")
    print(traceback.format_exc())
    print("> END OF TRACEBACK\n")
finally:
    sys.exit(0)
