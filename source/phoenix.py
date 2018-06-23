#!/usr/bin/env python3
import sys, socket, ssl, hashlib, getpass, time

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock = ssl.wrap_socket(ircsock, ssl_version=ssl.PROTOCOL_TLSv1_2, ciphers="DHE-RSA-AES256-GCM-SHA384")
server = "chat.freenode.net" # Server
channel = "##SRM-OSC" # Channel
botnick = "PhoenixSRM"
adminname = ["SPYR4D4R", "toxicmender"] # Admins that can shutdown the bot
exitcode = "bye " + botnick

# Get the bot password from user, only admins know this password
# Password is required to verify the botnick
md5_pass = ""
password = ""
attempt = 0
while attempt < 3 and md5_pass != "0526247a6e1674fc61bb70d28688b908":
    try:
        password = getpass.getpass(f"\n Enter Bot Password [Attempt: {attempt + 1}/3]: ")
        md5_pass = str(hashlib.md5(password.encode("utf-8")).hexdigest())
        attempt += 1
    except:
        print("\n Failed to get correct password. Exiting...")
        sys.exit(0)
if md5_pass == "0526247a6e1674fc61bb70d28688b908":
    print("\n Password verified. Connecting to Freenode IRC")
else:
    print("\n Incorrect password. Exiting...")
    sys.exit(0)

# Start connection to Freenode IRC
ircsock.connect((server, 6697)) # SSL Port 6697
ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " " + botnick + "\n", "UTF-8"))
ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))
ircsock.send(bytes("NickServ IDENTIFY " + password + "\n", "UTF-8"))

# join channel(s)
def joinchan(chan):
    ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))

# respond to server Pings.
def ping():
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

# sends messages to the target.
def sendmsg(msg, target=channel):
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

# sends help info as a private message to the user
def help(target, topic="all"):

    # recursive function to print messages in intended form
    def nester(messagelist, level=1, delay=0):
        for each_message in messagelist:
            if isinstance(each_message, list):
                nester(each_message, level+1, delay)
            else:
                for tabs in range(level):
                    each_message = "\t" + each_message
                time.sleep(delay)
                sendmsg(each_message, target)

    # syntax flag is for wrong syntax
    syntax = ["Wrong Syntax",
    ["-> Use .help basics", "-> Use .help nick"]]

    # basic flag for basic commands
    basics = ["## The Basics",
    ["/join #channel", ["+ Joins the specified channel."]],
    ["/part #channel", ["+ Leaves the specified channel."]],
    ["/quit [message]", ["+ Disconnects from current server with optional leaving message."]],
    ["/server hostname", ["+ Connects to the specified server."]],
    ["/sslserver hostname", ["+ Connects to the specified server over ssl."]],
    ["/list", ["+ Lists all the channels on the current network."]],
    ["/nick nickname", ["+ Changes your nick."]],
    ["/names #channel", ["+ Shows the nicks of all users on #channel."]],
    ["/msg nickname message", ["+ Sends a private messafe to a user."]],
    ["/query nickname message", ["+ Sends a private message to a user and opens a private chat window."]],
    ["/me action", ["+ Prints 'yourname action'."]],
    ["/notice nickname message", ["+ Sends a notice to the specified user.", "+ Like /msg, but usually with sound."]],
    ["/whois nickname", ["+ Shows information about the specified user.", "+ This action is not visible to the specified user."]],
    ["/whowas nickname", ["+ Shows information about a user who has quit."]],
    ["/ping nickname", ["+ Pings the specified user.", "+ This action is visible to the specified user."]]]

    nick = ["## Nick Management",
    ["/nickserv register password [email]", ["+ Registers your current nick with NickServ,", "+ With the chosen password and binds it to an email address."]],
    ["/nickserv identify password", ["+ Identifies your nick to NickServ using the password you set.", "+ If you have a nick that's been registered."]],
    ["/nickserv recover nickname password", ["+ Kills(forcibly disconnects) someone who has your registered nick."]],
    ["/nickserv ghost nickname password", ["+ Terminates a 'ghost' IRC session that's using your nickname."]],
    ["/nickserv set password yournewpassword", ["+ Changes your password."]]]

    if topic == "all":
        messagelist = syntax + basics + nick
        nester(messagelist, delay=2)
    elif topic == "basics":
        nester(basics, delay=2)
    elif topic == "nick":
        nester(nick, delay=1)
    else:
        nester(syntax)

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
                if message == ".help":
                    help(target=name)
                elif message[:5].find('.help') != -1:
                    if message.find(' ') != -1:
                        topic = message.split(' ', 1)[1].rstrip()
                        if topic in ["all", "basics", "nick"]:
                            help(name, topic)
                        else:
                            help(channel, "syntax")
                    else:
                        help(channel, "syntax")
                elif message[:5].find('.tell') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    else:
                        target = name
                        message = "Could not parse. Use .tell <target> <message>"
                    sendmsg(target + " : " + name + " says " + message)
            if name.lower() in [a.lower() for a in adminname] and message.rstrip() == exitcode:
                sendmsg("oh...okay. :'(")
                ircsock.send(bytes("QUIT \n", "UTF-8"))
                return
        else:
            if ircmsg.find("PING :") != -1:
                ping()

try:
    main()
except KeyboardInterrupt:
    sendmsg("oops my computer went down... *_*")
    sys.exit(0)
