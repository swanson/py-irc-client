import irclib
import sys
from Tkinter import *
import tkSimpleDialog
from tkMessageBox import *
import threading
import string
import bisect
import re
import getpass
from time import localtime, strftime


def spin():
  global done, irc
  while done == 0:
    irc.process_once(0.2)
  sys.exit(0)

def die():
  global done
  done = 1
  sys.exit(0)

global ServerNick
global DefaultServer
#UNCOMMENT THIS
ServerNick=getpass.getuser()
#ServerNick="YOURNAMEHERE"
DefaultServer="irc.freenode.net"

global ListList
ListList=[]

root=Tk()
#CHANGE THIS
root.title("Not connected")

irc=irclib.IRC()
server=irc.server()

def on_join(conn, event):
  global ServerNick
  Str="*** " + event.source() + " joined " + event.target() + "\n"
  Person=event.source()
  Person=Person.split("!")
  X=WindowDict.get(string.lower(event.target()))
  X.Channel.config(state=NORMAL)
  X.Channel.insert(END, Str, "join")
  scroll_down(X.Channel)
  X.Channel.config(state=DISABLED)
  if Person[0]==ServerNick:
    pass
  else:
    Person=event.source()
    Person=Person.split("!")
    X.AddUser(Person[0])

def on_part(conn, event):
  global ServerNick
  Str="*** " + event.source() + " left " + event.target() + "\n"
  Person=event.source()
  Person=Person.split("!")
  if Person[0]==ServerNick:
    pass
  else:
    try:
      X=WindowDict.get(string.lower(event.target()))
      X.Channel.config(state=NORMAL)
      X.Channel.insert(END, Str, "leave")
      scroll_down(X.Channel)
      X.Channel.config(state=DISABLED)
      Person=event.source()
      Person=Person.split("!")
      X.RemoveUser(Person[0])
    except:
      pass

def on_quit(conn, event):
  Reason=event.arguments()
  Person=event.source()
  Person=Person.split("!")
  Windows=WindowDict.values()
  Str="*** "+event.source()+" quit IRC ("+Reason[0]+")\n"
  for I in Windows:
    I.UserQuit(Person[0], Str)

def on_pubmsg(conn, event):
  time=MakeTimeStamp()
  Nick=event.source()
  Nick=Nick.split("!")
  Text=event.arguments()
  Str=time+"<"+Nick[0]+"> "+Text[0]+"\n"
  X=WindowDict.get(string.lower(event.target()))
  if X != None:
    X.Channel.config(state=NORMAL)
    X.Channel.insert(END, Str)
    scroll_down(X.Channel)
    X.Channel.config(state=DISABLED)

def on_privmsg(conn, event):
  Nick=event.source()
  Nick=Nick.split("!")
  Text=event.arguments()
  time=MakeTimeStamp()
  Str=time+"<"+Nick[0]+"> "+Text[0]+"\n"
  X=PMDict.get(string.lower(Nick[0]))
  if X == None:
    X=PMWindow(Nick[0])
  print PMDict
  X.List.config(state=NORMAL)
  X.List.insert(END, Str)
  scroll_down(X.List)
  X.List.config(state=DISABLED)

def on_name(conn, event):
  RawUsers=event.arguments()
  X=WindowDict.get(string.lower(RawUsers[1]))
  UserList=RawUsers[2]
  UserList=UserList.split()
  UserList.sort()
  for I in range(len(UserList)):
    X.Users.insert(END, UserList[I])
    X.UserList.append(UserList[I])
  X.UserList.sort()

def on_ctopic(conn, event):
  Raw=event.arguments()
  X=WindowDict.get(string.lower(Raw[0]))
  Topic=Raw[0]+" - "+Raw[1]
  # UNCOMMENT THIS WINDOWS THREADING ERROR
  X.Window.title(Topic)
  Str="*** Welcome to: "+Raw[0]+". Current topic is: "+Raw[1]+"\n"
  X.Channel.config(state=NORMAL)
  X.Channel.insert(END, Str, "topic")
  scroll_down(X.Channel)
  X.Channel.config(state=DISABLED)

def on_topic(conn, event):
  Person=event.source()
  Person=Person.split("!")
  Raw=event.arguments()
  X=WindowDict.get(string.lower(event.target()))
  Topic=event.target()+" - "+Raw[0]
  Str="*** "+Person[0]+" changes topic to '"+Raw[0]+"'\n"
  # UNCOMMENT THIS WINDOWS THREADING ERROR
  X.Window.title(Topic)
  X.Channel.config(state=NORMAL)
  X.Channel.insert(END, Str, "topic")
  scroll_down(X.Channel)
  X.Channel.config(state=DISABLED)

def on_list_start(conn, event):
  global ListList
  del ListList
  newtitle=server.get_server_name()
  newtitle="Channel listing for "+newtitle
  ListList=[]
  ChanList.delete(0, END)
  # UNCOMMENT THIS WINDOWS THREADING ERROR
  ChannelList.deiconify()
  ChannelList.title(newtitle)

def on_list(conn, event):
  global ListList
  Raw=event.arguments()
  Str=Raw[0]+" "+Raw[1]+" "+Raw[2]
  ListList.append(Str)
  ChanList.insert(END, Str)

def joinchan(conn):
  Raw=ChanList.get(ACTIVE)
  Raw=Raw.split()
  if WindowDict.has_key(string.lower(Raw[0])):
    pass
  else:
    X=ChatWindow(string.lower(Raw[0]))
    server.join(Raw[0])

def on_nick(conn, event):
  Windows=WindowDict.values()
  if Windows == None:
    return
  Raw=event.source()
  Raw=Raw.split("!")
  OldNick=Raw[0]
  NewNick=event.target()
  for I in Windows:
    I.NickChange(OldNick, NewNick)

def on_action(conn, event):
  X=WindowDict.get(string.lower(event.target()))
  Raw=event.source()
  Raw=Raw.split("!")
  Person=Raw[0]
  Raw=event.arguments()
  Action=Raw[0]
  Str="*** "+Person+" "+Action+"\n"
  X.Channel.config(state=NORMAL)
  X.Channel.insert(END, Str, "emote")
  scroll_down(X.Channel)
  X.Channel.config(state=DISABLED)

def on_opneeded(conn, event):
  Raw=event.arguments()
  channel=Raw[0]
  message=Raw[1]
  Str="*** "+message+"\n"
  X=WindowDict.get(string.lower(channel))
  if X != None:
    X.Channel.config(state=NORMAL)
    X.Channel.insert(END, Str, "topic")
    scroll_down(X.Channel)
    X.Channel.config(state=DISABLED)
  else:
    List.config(state=NORMAL)
    List.insert(END, Str)
    scroll_down(List)
    List.config(state=DISABLED)

def on_mode(conn, event):
  channel=event.target()
  Raw=event.source()
  Raw=Raw.split("!")
  nick=Raw[0]
  Raw=event.arguments()
  mode=Raw[0]
  target2=Raw[1]
  target=""
  for I in range(1, len(Raw)):
    target=target+" "+Raw[I]
  Str="*** "+nick+" sets mode: "+mode+" "+target+"\n"
  X=WindowDict.get(string.lower(channel))
  if X != None:
    X.Channel.config(state=NORMAL)
    X.Channel.insert(END, Str, "topic")
    scroll_down(X.Channel)
    X.Channel.config(state=DISABLED)
    if mode == "+o":
      X.RemoveUser(target2)
      ntarget="@"+target2
      X.AddUser(ntarget)
    elif mode == "-o":
      X.RemoveUser(target2)
      X.AddUser(target2)

def on_kick(conn, event):
  global ServerNick
  Raw=event.source()
  Raw=Raw.split("!")
  op=Raw[0]
  Raw=event.arguments()
  target=Raw[0]
  message=Raw[1]
  if message==op:
    message="No reason given"
  Str="*** "+target+" was kicked by "+op+" ("+message+")\n"
  X=WindowDict.get(string.lower(event.target()))
  if target != ServerNick:
    X.Channel.config(state=NORMAL)
    X.Channel.insert(END, Str, "leave")
    scroll_down(X.Channel)
    X.RemoveUser(target)
    X.Channel.config(state=DISABLED)
  else:
    CloseWindow(event.target())
    List.config(state=NORMAL)
    List.insert(END, Str)
    scroll_down(List)
    List.config(state=DISABLED)

def on_privnotice(conn, event):
  global ServerNick
  Raw=event.source()
  Raw=Raw.split("!")
  source=Raw[0]
  dest=event.target()
  Raw=event.arguments()
  Msg=Raw[0]
  time=MakeTimeStamp()
  Str=time+"-"+source+"- "+Msg+"\n"
  if ServerNick == dest:
    List.config(state=NORMAL)
    List.insert(END, Str)
    scroll_down(List)
    List.config(state=DISABLED)

def shandler(conn, event):
  List.config(state=NORMAL)
  List.insert(END, "*** " + string.join(event.arguments(), ' ')
+ "\n")
  scroll_down(List)
  List.config(state=DISABLED)

def scroll_down(obj):
  obj.yview_moveto(1)

def prompt_exit():
  Sure=askyesno("Exit?", "Do you really want to exit?")
  if Sure == True:
    die()
  else:
    return

done=0
WindowDict={}
PMDict={}

def callback(channel):
  X=WindowDict.get(channel)
  del WindowDict[string.lower(channel)]
  server.part(channel)
  X.Window.destroy()

class ChatWindow:
  def __init__(Self, channelname):
    WindowDict[string.lower(channelname)]=Self
    Self.ChannelName=string.lower(channelname)
    Self.Window=Toplevel()
    Self.Window.title(string.lower(channelname))
    Self.Window.protocol("WM_DELETE_WINDOW", lambda x=channelname: callback(x))
    Self.Message=Entry(Self.Window, bg="#676760", fg="#f7f7f7", font=("Courier New", 12))
    Self.Message.bind("<Return>", Self.SendMsgChat)
    Self.Message.grid(column=0, columnspan=6, row=2, sticky=W+E+S)
    Self.Channel=Text(Self.Window, bg="#676760", fg="#f7f7f7", font=("Courier New", 12))
    Self.Channel.tag_config("emote", foreground="#6188f8")
    Self.Channel.tag_config("join", foreground="#18dd03")
    Self.Channel.tag_config("leave", foreground="#F5003D")
    Self.Channel.tag_config("topic", foreground="#fefe00")
    Self.Channel.config(state=DISABLED)
    Self.Channel.grid(column=0, row=1, columnspan=3, sticky=N+S+E+W)
    Self.Vscroll=Scrollbar(Self.Window, command=Self.Channel.yview, bg="#7f0303", troughcolor="#cc2b00")
    Self.Vscroll.grid(column=3,row=1,sticky=N+S)
    Self.Channel["yscrollcommand"]=Self.Vscroll.set
    Self.Users=Listbox(Self.Window, bg="#676760", fg="#f7f7f7", font=("Courier New", 12))
    Self.Users.bind("<Double-Button-1>", Self.PM)
    Self.Users.grid(column=4,row=1,sticky=N+S+E+W)
    Self.Vscroll2=Scrollbar(Self.Window, command=Self.Users.yview, bg="#7f0303", troughcolor="#cc2b00")
    Self.Vscroll2.grid(column=5, row=1, sticky=N+S)
    Self.Users["yscrollcommand"]=Self.Vscroll2.set
    Self.Window.columnconfigure(2, weight=1)
    Self.Window.rowconfigure(1, weight=1)
    Self.UserList=[]
    server.join(channelname)

    Self.File=Menubutton(Self.Window, text="File")
    Self.File.grid(column=0, row=0, sticky=N+W)
    Self.File.menu=Menu(Self.File, tearoff=0)
    Self.File["menu"]=Self.File.menu
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Connect", command=Connect)
    Self.File.menu.add_command(label="Disonnect", command=Disconnect)
    Self.File.menu.entryconfigure(1, state=DISABLED)
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Select server...", command=SelectServer)
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Exit", command=prompt_exit)

    Self.Commands=Menubutton(Self.Window, text="Commands")
    Self.Commands.grid(column=1, row=0, stick=N+W)
    Self.Commands.menu=Menu(Self.Commands, tearoff=0)
    Self.Commands["menu"]=Self.Commands.menu
    Self.Commands.menu.add_separator()
    Self.ServerRelated=Menu(Self.Commands, tearoff=0)
    Self.ServerRelated.add_separator()
    Self.ServerRelated.add_command(label="Get channel listing...", command=MenuList)
    Self.ServerRelated.add_command(label="Change nick...", command=MenuNick)
    Self.Commands.menu.add_cascade(label="Server related", menu=Self.ServerRelated)
    Self.ChannelRelated=Menu(Self.Commands, tearoff=0)
    Self.ChannelRelated.add_separator()
    Self.ChannelRelated.add_command(label="Join channel...", command=MenuJoin)
    Self.ChannelRelated.add_command(label="Part channel...", command=Self.MenuPart)
    Self.ChannelRelated.add_separator()
    Self.ChannelRelated.add_command(label="Kick user...", command=Self.MenuKick)
    Self.Commands.menu.add_cascade(label="Channel related", menu=Self.ChannelRelated)

    Self.Help=Menubutton(Self.Window, text="Help")
    Self.Help.grid(column=2, row=0, sticky=N+W)
    Self.Help.menu=Menu(Self.Help, tearoff=0)
    Self.Help["menu"]=Self.Help.menu
    Self.Help.menu.add_separator()
    Self.Help.menu.add_command(label="About", command=ShowAbout)

    Self.Window.mainloop()

  def SendMsgChat(Self, event):
    global ServerNick
    Msg=Self.Message.get()
    Msg=Msg.split()
    if len(Msg) == 0:
      pass
    elif Msg[0] == "/join":
      if len(Msg) > 1:
        Self.Message.delete(0, END)
        X=ChatWindow(string.lower(Msg[1]))
        server.join(Msg[1])
      Self.Message.delete(0, END)
    elif Msg[0] == "/part":
      if len(Msg) > 1:
        Self.Message.delete(0, END)
        server.part(Msg[1])
        CloseWindow(string.lower(Msg[1]))
    elif Msg[0] == "/list":
      server.list()
      Self.Message.delete(0, END)
    elif Msg[0] == "/nick":
      if len(Msg) > 1:
        server.nick(Msg[1])
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/topic":
      if len(Msg) > 2:
        dest=Msg[1]
        Str=""
        for I in range(2, len(Msg)):
          Str=Str+Msg[I]+" "
        Str=Str.rstrip()
        server.topic(dest, Str)
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/me":
      global ServerNick
      if len(Msg) > 1:
        Str=""
        for I in range(1, len(Msg)):
          Str=Str+Msg[I]+" "
        server.action(Self.ChannelName, Str)
        Str2="*** "+ServerNick+" "+Str+"\n"
        Self.Channel.config(state=NORMAL)
        Self.Channel.insert(END, Str2, "emote")
        scroll_down(Self.Channel)
        Self.Channel.config(state=DISABLED)
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/whois":
      WhoList=[]
      for I in range(1, len(Msg)):
        WhoList.append(Msg[I])
      if len(WhoList) > 0:
        server.whois(WhoList)
      Self.Message.delete(0, END)
    elif Msg[0] == "/notice":
      if len(Msg) > 2:
        dest=Msg[1]
        Str=""
        for I in range(2, len(Msg)):
          Str=Str+Msg[I]+" "
        Str=Str.rstrip()
        server.notice(dest, Str)
        Self.Message.delete(0, END)
        Self.Channel.config(state=NORMAL)
        Str2="-> -"+dest+"- "+Str+"\n"
        Self.Channel.insert(END, Str2)
        scroll_down(Self.Channel)
        Self.Channel.config(state=DISABLED)
      Self.Message.delete(0, END)
    elif Msg[0] == "/msg":
      if len(Msg) > 2:
        target=Msg[1]
        text=""
        for I in range(2, len(Msg)):
          text=text+Msg[I]+" "
        text=text.rstrip()
        server.privmsg(target, text)
        X=PMDict.get(string.lower(target))
        if X == None:
          X=PMWindow(target)
        time=MakeTimeStamp()
        Str=time+"<"+ServerNick+"> "+text+"\n"
        X.List.config(state=NORMAL)
        X.List.insert(END, Str)
        scroll_down(X.List)
        X.List.config(state=DISABLED)
        X.Window.lift()
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/kick":
      if len(Msg) > 2:
        chan=Msg[1]
        vict=Msg[2]
        reason=""
        for I in range(3, len(Msg)):
          reason=reason+Msg[I]+" "
        reason=reason.rstrip()
        server.kick(chan, vict, reason)
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/mode":
      if len(Msg) > 2:
        chan=Msg[1]
        mode=Msg[2]
        args=""
        for I in range(3, len(Msg)):
          args=args+Msg[I]+" "
        args=args.rstrip()
        Str=mode+" "+args
        server.mode(chan, Str)
        Self.Message.delete(0, END)
      Self.Message.delete(0, END)
    elif Msg[0] == "/exit":
      Sure=askyesno("Exit?", "Do you really want to exit?")
      if Sure == True:
        die()
      else:
        pass
    elif re.match("^\/.", Msg[0]):
      Self.Message.delete(0, END)
    else:
      server.privmsg(Self.ChannelName, Self.Message.get())
      time=MakeTimeStamp()
      Str=time+"<"+ServerNick+"> "+Self.Message.get()+"\n"
      Self.Channel.config(state=NORMAL)
      Self.Channel.insert(END, Str)
      scroll_down(Self.Channel)
      Self.Channel.config(state=DISABLED)
      Self.Message.delete(0, END)

  def NickChange(Self, Old, New):
    global ServerNick
    if Old == ServerNick:
      ServerNick=New
    Str="*** "+Old+" is now known as "+New+"\n"
    Old2="@"+Old
    New2="@"+New
    for I in range(len(Self.UserList)):
      if Self.UserList[I] == Old:
        Self.RemoveUser(Old)
        Self.AddUser(New)
        Self.Channel.config(state=NORMAL)
        Self.Channel.insert(END, Str)
        scroll_down(Self.Channel)
        Self.Channel.config(state=DISABLED)
      elif Self.UserList[I] == Old2:
        Self.RemoveUser(Old)
        Self.AddUser(New2)
        Self.Channel.config(state=NORMAL)
        Self.Channel.insert(END, Str)
        scroll_down(Self.Channel)
        Self.Channel.config(state=DISABLED)

  def AddUser(Self, user):
    bisect.insort(Self.UserList, user)
    Self.UserList.sort()
    Self.UpdateUsers()

  def RemoveUser(Self, user):
    user2="@"+user
    for I in range(len(Self.UserList)):
      if Self.UserList[I] == user:
        del Self.UserList[I]
        break
      elif Self.UserList[I] == user2:
        del Self.UserList[I]
        break
    Self.UserList.sort()
    Self.UpdateUsers()

  def UserQuit(Self, user, text):
    for I in range(len(Self.UserList)):
      if Self.UserList[I] == user:
        Self.Channel.config(state=NORMAL)
        Self.Channel.insert(END, text, "leave")
        scroll_down(Self.Channel)
        Self.Channel.config(state=DISABLED)
        del Self.UserList[I]
        Self.UpdateUsers()
        break
    Self.UserList.sort()

  def UpdateUsers(Self):
    Self.Users.delete(0, END)
    Self.UserList.sort()
    for I in range(len(Self.UserList)):
      Self.Users.insert(END, Self.UserList[I])

  def PM(Self, conn):
    Raw=Self.Users.get(ACTIVE)
    print Raw[0]
    tar=""
    if Raw[0] == "@":
      tar=Raw[1:]
    X=PMDict.get(string.lower(tar))
    if X == None:
      X=PMWindow(tar)
    X.Window.lift()

  def MenuPart(Self):
    server.part(Self.ChannelName)
    CloseWindow(string.lower(Self.ChannelName))

  def MenuKick(Self):
    target=tkSimpleDialog.askstring("Kick User", "Enter victim's nick:")
    if len(target) == 0:
      return
    reason=tkSimpleDialog.askstring("Kick Reason", "Enter reason (if any):")
    try:
      if len(reason) == 0:
        reason=""
      server.kick(Self.ChannelName, target, reason)
    except:
      pass

class PMWindow:
  def __init__(Self, nick):
    PMDict[string.lower(nick)]=Self
    Self.Window=Toplevel()
    Self.Window.title(nick)
    Self.Nick=nick
    Self.EntryBox=Entry(Self.Window, bg="#676760", fg="#f7f7f7", font=("Courier New",12))
    Self.EntryBox.bind("<Return>", Self.SendPM)
    Self.EntryBox.grid(column=0, row=2, columnspan=5, sticky=S+W+E)
    Self.List=Text(Self.Window, bg="#676760", fg="#f7f7f7", font=("Courier New",12))
    Self.List.grid(column=0, row=1, columnspan=4, sticky=N+S+E+W)
    Self.Vscroll=Scrollbar(Self.Window, command=Self.List.yview, bg="#7f0303", troughcolor="#cc2b00")
    Self.Vscroll.grid(column=4, row=1, sticky=N+S)
    Self.Window.columnconfigure(3, weight=1)
    Self.Window.rowconfigure(1, weight=1)
    Self.List["yscrollcommand"]=Self.Vscroll.set
    Self.List.config(state=DISABLED)

    Self.File=Menubutton(Self.Window, text="File")
    Self.File.grid(column=0, row=0, sticky=N+W)
    Self.File.menu=Menu(Self.File, tearoff=0)
    Self.File["menu"]=Self.File.menu
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Connect", command=Connect)
    Self.File.menu.add_command(label="Disonnect", command=Disconnect)
    Self.File.menu.entryconfigure(1, state=DISABLED)
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Select server...", command=SelectServer)
    Self.File.menu.add_separator()
    Self.File.menu.add_command(label="Exit", command=prompt_exit)

    Self.Commands=Menubutton(Self.Window, text="Commands")
    Self.Commands.grid(column=1, row=0, stick=N+W)
    Self.Commands.menu=Menu(Self.Commands, tearoff=0)
    Self.Commands["menu"]=Self.Commands.menu
    Self.Commands.menu.add_separator()
    Self.ServerRelated=Menu(Self.Commands, tearoff=0)
    Self.ServerRelated.add_separator()
    Self.ServerRelated.add_command(label="Get channel listing...", command=MenuList)
    Self.ServerRelated.add_command(label="Change nick...", command=MenuNick)
    Self.Commands.menu.add_cascade(label="Server related", menu=Self.ServerRelated)
    Self.ChannelRelated=Menu(Self.Commands, tearoff=0)
    Self.ChannelRelated.add_separator()
    Self.ChannelRelated.add_command(label="Join channel...", command=MenuJoin)
    Self.ChannelRelated.add_command(label="Part channel...", command=MenuPart)
    Self.ChannelRelated.add_separator()
    Self.ChannelRelated.add_command(label="Kick user...", command=MenuKick2)
    Self.Commands.menu.add_cascade(label="Channel related", menu=Self.ChannelRelated)

    Self.Help=Menubutton(Self.Window, text="Help")
    Self.Help.grid(column=2, row=0, sticky=N+W)
    Self.Help.menu=Menu(Self.Help, tearoff=0)
    Self.Help["menu"]=Self.Help.menu
    Self.Help.menu.add_separator()
    Self.Help.menu.add_command(label="About", command=ShowAbout)

  def SendPM(Self, event):
    global ServerNick
    Msg=Self.EntryBox.get()
    Msg2=Self.EntryBox.get()
    Msg=Msg.split()
    Self.EntryBox.delete(0, END)
    if len(Msg) == 0:
      pass
    elif Msg[0] == "/join":
      if len(Msg) > 1:
        X=ChatWindow(string.lower(Msg[1]))
        server.join(Msg[1])
    elif Msg[0] == "/part":
      if len(Msg) > 1:
        server.part(Msg[1])
        CloseWindow(string.lower(Msg[1]))
    elif Msg[0] == "/msg":
      global ServerNick
      if len(Msg) > 2:
        target=Msg[1]
        text=""
        for I in range(2, len(Msg)):
          text=text+Msg[I]+" "
        text=text.rstrip()
        X=PMDict.get(string.lower(target))
        if X == None:
          X=PMWindow(target)
        time=MakeTimeStamp()
        server.privmsg(target, text)
        Str=time+"<"+ServerNick+"> "+text+"\n"
        X.List.config(state=NORMAL)
        X.List.insert(END, Str)
        scroll_down(X.List)
        X.List.config(state=DISABLED)
        X.Window.lift()
    elif Msg[0] == "/exit":
      Sure=askyesno("Exit?", "Do you really want to exit?")
      if Sure == True:
        die()
      else:
        pass
    elif re.match("^\/.", Msg[0]):
      pass
    else:
      time=MakeTimeStamp()
      server.privmsg(Self.Nick, Msg2)
      Str=time+"<"+ServerNick+"> "+Msg2+"\n"
      Self.List.config(state=NORMAL)
      Self.List.insert(END, Str)
      scroll_down(Self.List)
      Self.List.config(state=DISABLED)
      Self.EntryBox.delete(0, END)

def CloseWindow(channel):
    X=WindowDict.get(string.lower(channel))
    if X == None:
      X=PMDict.get(string.lower(channel))
      if X == None:
        pass
      else:
        del PMDict[string.lower(channel)]
        X.Window.destroy()
    else:
      del WindowDict[string.lower(channel)]
      print WindowDict
      X.Window.destroy()

def ShowAbout():
  About.deiconify()

def SendMsgSrv(event):
  global ServerNick
  global DefaultServer
  proceed=0
  Msg=EntryBox.get()
  EntryBox.delete(0, END)
  Msg=Msg.split()
  if server.is_connected() == True:
    proceed=1
  if len(Msg) == 0:
    return
  elif Msg[0] == "/join" and proceed == 1:
    if len(Msg) > 1:
      X=ChatWindow(Msg[1])
      server.join(Msg[1])
  elif Msg[0] == "/part" and proceed == 1:
    if len(Msg) > 1:
      server.part(Msg[1])
      CloseWindow(Msg[1])
  elif Msg[0] == "/list" and proceed == 1:
    server.list()
  elif Msg[0] == "/nick":
    if len(Msg) > 1:
      try:
        server.nick(Msg[1])
        ServerNick=Msg[1]
      except:
        ServerNick=Msg[1]
  elif Msg[0] == "/server":
    if len(Msg) > 1:
      DefaultServer=Msg[1]
      Connect()
  elif Msg[0] == "/topic" and proceed == 1:
    if len(Msg) > 2:
      dest=Msg[1]
      Str=""
      for I in range(2, len(Msg)):
        Str=Str+Msg[I]+" "
      Str=Str.rstrip()
      server.topic(dest, Str)
  elif Msg[0] == "/whois" and proceed == 1:
    WhoList=[]
    for I in range(1, len(Msg)):
      WhoList.append(Msg[I])
    if len(WhoList) > 0:
      server.whois(WhoList)
  elif Msg[0] == "/notice" and proceed == 1:
    if len(Msg) > 2:
      dest=Msg[1]
      Str=""
      for I in range(2, len(Msg)):
        Str=Str+Msg[I]+" "
      Str=Str.rstrip()
      server.notice(dest, Str)
      List.config(state=NORMAL)
      Str2="-> -"+dest+"- "+Str+"\n"
      List.insert(END, Str2)
      scroll_down(List)
      List.config(state=DISABLED)
  elif Msg[0] == "/msg" and proceed == 1:
    if len(Msg) > 2:
      target=Msg[1]
      text=""
      for I in range(2, len(Msg)):
        text=text+Msg[I]+" "
      text=text.rstrip()
      X=PMDict.get(string.lower(target))
      if X == None:
        X=PMWindow(target)
      time=MakeTimeStamp()
      server.privmsg(target, text)
      Str=time+"<"+ServerNick+"> "+text+"\n"
      X.List.config(state=NORMAL)
      X.List.insert(END, Str)
      scroll_down(X.List)
      X.List.config(state=DISABLED)
      X.Window.lift()
  elif Msg[0] == "/kick" and proceed == 1:
      if len(Msg) > 2:
        chan=Msg[1]
        vict=Msg[2]
        reason=""
        for I in range(3, len(Msg)):
          reason=reason+Msg[I]+" "
        reason=reason.rstrip()
        server.kick(chan, vict, reason)
  elif Msg[0] == "/mode" and proceed == 1:
      if len(Msg) > 2:
        chan=Msg[1]
        mode=Msg[2]
        args=""
        for I in range(3, len(Msg)):
          args=args+Msg[I]+" "
        args=args.rstrip()
        Str=mode+" "+args
        print Str
        server.mode(chan, Str)
  elif Msg[0] == "/exit":
    Sure=askyesno("Exit?", "Do you really want to exit?")
    if Sure == True:
      die()
    else:
      pass
  elif proceed == 0:
    List.config(state=NORMAL)
    List.insert(END, "Error: You are not connected to a server!\n")
    scroll_down(List)
    List.config(state=DISABLED)

def Connect():
  global ServerNick
  global DefaultServer
  global CurrentServer
  proceed=0
  try:
    server.connect(DefaultServer,6667,ServerNick)
    thread1 = threading.Thread(target=spin)
    thread1.start()
    proceed=1
  except irclib.ServerConnectionError, Message:
    Error=showwarning(title="Connect Error!", message=Message)
  if proceed==1:
    sname=server.get_server_name()
    #root.title(sname)
    CurrentServer=DefaultServer
    File.menu.entryconfigure(2, state=NORMAL)
    File.menu.entryconfigure(1, state=DISABLED)
    ServerRelated.entryconfigure(1, state=NORMAL)
    ChannelRelated.entryconfigure(1, state=NORMAL)
    ChannelRelated.entryconfigure(2, state=NORMAL)
    ChannelRelated.entryconfigure(4, state=NORMAL)

def Disconnect():
  global CurrentServer
  server.disconnect()
  List.config(state=NORMAL)
  scroll_down(List)
  List.insert(END, "*** Disconnected.\n")
  List.config(state=DISABLED)
  for I in WindowDict.keys():
    CloseWindow(I)
  for I in PMDict.keys():
    CloseWindow(I)
  File.menu.entryconfigure(1, state=NORMAL)
  File.menu.entryconfigure(2, state=DISABLED)
  ServerRelated.entryconfigure(1, state=DISABLED)
  ChannelRelated.entryconfigure(1, state=DISABLED)
  ChannelRelated.entryconfigure(2, state=DISABLED)
  ChannelRelated.entryconfigure(4, state=DISABLED)

def MakeTimeStamp():
  Time=strftime("%H:%M:%S", localtime())
  Str="["+Time+"] "
  return Str


def SelectServer():
  global DefaultServer
  New=tkSimpleDialog.askstring("Change Default Server", "Enter server name:")
  if New != None:
    DefaultServer=New

def MenuJoin():
  Channel=tkSimpleDialog.askstring("Join New Channel", "Enter channel name:")
  if Channel != None:
    print Channel
    X=WindowDict.get(string.lower(Channel))
    if X == None:
      X=ChatWindow(string.lower(Channel))
      server.join(Channel)
    else:
      X.Window.lift()

def MenuPart():
  Channel=tkSimpleDialog.askstring("Part Channel", "Enter channel name:")
  if Channel != None:
    server.part(Channel)
    CloseWindow(Channel)

def MenuList():
  server.list()

def MenuNick():
  global ServerNick
  Nick=tkSimpleDialog.askstring("Change Nick", "Enter new nick:")
  try:
    server.nick(Nick)
    ServerNick=Nick
  except:
    ServerNick=Nick

def MenuKick2():
  chan=tkSimpleDialog.askstring("Channel Name", "Enter channel name:")
  if chan == None:
    return
  target=tkSimpleDialog.askstring("Kick User", "Enter victim's nick:")
  if target == None:
    return
  reason=tkSimpleDialog.askstring("Kick Reason", "Enter reason (if any):")
  try:
    if reason == None:
      reason=""
    server.kick(chan, target, reason)
  except:
    pass

def FilterList(conn):
  global ListList
  global Default
  if Default == 1:
    Regex="^#ece([0]?3[7-9]|[0]?[4-9][0-9]|[1-3][0-9][0-9]|4[0-2][0-9]|43[0-7])[^0-9]"
  else:
    Regex=FilterEntry.get()
  if len(Regex) == 0:
    Regex="."
  ChanList.config(state=NORMAL)
  ChanList.delete(0, END)
  for I in ListList:
    try:
      if re.match(Regex, I) != None:
        ChanList.insert(END, I)
    except:
      pass

def DefaultFilter():
  global Default
  if Default==1:
    Default=0
  else:
    Default=1
  FilterList("")

server.add_global_handler("join", on_join)
server.add_global_handler("part", on_part)
server.add_global_handler("quit", on_quit)
server.add_global_handler("pubmsg", on_pubmsg)
server.add_global_handler("privmsg", on_privmsg)
server.add_global_handler("namreply", on_name)
server.add_global_handler("currenttopic", on_ctopic)
server.add_global_handler("topic", on_topic)
server.add_global_handler("liststart", on_list_start)
server.add_global_handler("list", on_list)
server.add_global_handler("nick", on_nick)
server.add_global_handler("action", on_action)
server.add_global_handler("chanoprivsneeded", on_opneeded)
#server.add_global_handler("privnotice", on_privnotice)
server.add_global_handler("mode", on_mode)
server.add_global_handler("kick", on_kick)
server.add_global_handler("yourhost", shandler)
server.add_global_handler("created", shandler)
server.add_global_handler("myinfo", shandler)
server.add_global_handler("featurelist", shandler)
server.add_global_handler("luserclient", shandler)
server.add_global_handler("luserop", shandler)
server.add_global_handler("luserchannels", shandler)
server.add_global_handler("luserme", shandler)
server.add_global_handler("n_local", shandler)
server.add_global_handler("n_global", shandler)
server.add_global_handler("luserconns", shandler)
server.add_global_handler("luserunknown", shandler)
server.add_global_handler("welcome", shandler)
server.add_global_handler("motd", shandler)
server.add_global_handler("nosuchnick", shandler)
server.add_global_handler("nosuchchannel", shandler)
server.add_global_handler("whoisuser", shandler)
server.add_global_handler("endofwhois", shandler)

About=Toplevel(bg="#676760")
About.title("eceIRC-XP.py --- ECE364 Final Project")
About.maxsize(width=410, height=400)
About.resizable(width=0, height=0)
About.protocol("WM_DELETE_WINDOW", lambda: About.withdraw())
ascii=Text(About, bg="#676760", fg="#f7f7f7", font=("Courier New",12))
ascii.insert(END,"Matt Swanson  mdswanso@purdue.edu  Sp08\n")
ascii.insert(END,"              .,-:;//;:=,\n")
ascii.insert(END,"           . :H@@@MM@M#H/.,+%;,\n")
ascii.insert(END,"       ,/X+ +M@@M@MM%=,-%HMMM@X/,\n")
ascii.insert(END,"     -+@MM; $M@@MH+-,;XMMMM@MMMM@+-\n")
ascii.insert(END,"    ;@M@@M- XM@X;. -+XXXXXHHH@M@M#@/.\n")
ascii.insert(END,"  ,%MM@@MH ,@%=            .---=-=:=,.\n")
ascii.insert(END,"  =@#@@@MX .,              -%HX$$%%%+;\n")
ascii.insert(END," =-./@M@M$    Powered by:   .;@MMMM@MM:\n")
ascii.insert(END," X@/ -$MM/                    .+MM@@@M$\n")
ascii.insert(END,",@M@H: :@:                    . =X#@@@@-\n")
ascii.insert(END,",@@@MMX,.   Aperture Science  /H- ;@M@M=\n")
ascii.insert(END,".H@@@@M@+,                    %MM+..%#$.\n")
ascii.insert(END," /MMMM@MMH/.                  XM@MH; =;\n")
ascii.insert(END,"  /%+%$XHH@$=              , .H@@@@MX,\n")
ascii.insert(END,"   .=--------.           -%H.,@@@@@MX,\n")
ascii.insert(END,"   .%MM@@@HHHXX$$$%+- .:$MMX =M@@MM%.\n")
ascii.insert(END,"     =XMMM@MM@MM#H;,-+HMM@M+ /MMMX=\n")
ascii.insert(END,"       =%@M@M#@$-.=$@MM@@@M; %M%=\n")
ascii.insert(END,"         ,:+$+-,/H#MMMMMMM@= =,\n")
ascii.insert(END,"               =++%%%%+/:-.\n")
ascii.insert(END,"            The cake is a lie")
ascii.config(state=DISABLED)
ascii.grid(row=0, column=0, sticky=N+S+E+W)
About.rowconfigure(0, weight=1)
About.columnconfigure(0, weight=1)
About.withdraw()

root.protocol("WM_DELETE_WINDOW", lambda: die())
EntryBox=Entry(root, bg="#676760", fg="#f7f7f7", font=("Courier New",12))
EntryBox.bind("<Return>", SendMsgSrv)
EntryBox.grid(column=0, row=2, columnspan=5, sticky=S+W+E)
List=Text(root, bg="#676760", fg="#f7f7f7", font=("Courier New",12))
List.grid(column=0, row=1, columnspan=4, sticky=N+S+E+W)
Vscroll=Scrollbar(root, command=List.yview, bg="#7f0303", troughcolor="#cc2b00")
Vscroll.grid(column=4, row=1, sticky=N+S)
root.columnconfigure(3, weight=1)
root.rowconfigure(1, weight=1)
List["yscrollcommand"]=Vscroll.set
List.config(state=DISABLED)
File=Menubutton(root, text="File")
File.grid(column=0, row=0, sticky=N+W)
File.menu=Menu(File, tearoff=0)
File["menu"]=File.menu
File.menu.add_separator()
File.menu.add_command(label="Connect", command=Connect)
File.menu.add_command(label="Disonnect", command=Disconnect)
File.menu.entryconfigure(2, state=DISABLED)
File.menu.add_separator()
File.menu.add_command(label="Select server...", command=SelectServer)
File.menu.add_separator()
File.menu.add_command(label="Exit", command=prompt_exit)

Commands=Menubutton(root, text="Commands")
Commands.grid(column=1, row=0, stick=N+W)
Commands.menu=Menu(Commands, tearoff=0)
Commands["menu"]=Commands.menu
Commands.menu.add_separator()
ServerRelated=Menu(Commands, tearoff=0)
ServerRelated.add_separator()
ServerRelated.add_command(label="Get channel listing...", command=MenuList)
ServerRelated.entryconfigure(1, state=DISABLED)
ServerRelated.add_command(label="Change nick...", command=MenuNick)
Commands.menu.add_cascade(label="Server related", menu=ServerRelated)
ChannelRelated=Menu(Commands, tearoff=0)
ChannelRelated.add_separator()
ChannelRelated.add_command(label="Join channel...", command=MenuJoin)
ChannelRelated.entryconfigure(1, state=DISABLED)
ChannelRelated.add_command(label="Part channel...", command=MenuPart)
ChannelRelated.entryconfigure(2, state=DISABLED)
ChannelRelated.add_separator()
ChannelRelated.add_command(label="Kick user...", command=MenuKick2)
ChannelRelated.entryconfigure(4, state=DISABLED)
Commands.menu.add_cascade(label="Channel related", menu=ChannelRelated)

Help=Menubutton(root, text="Help")
Help.grid(column=2, row=0, sticky=N+W)
Help.menu=Menu(Help, tearoff=0)
Help["menu"]=Help.menu
Help.menu.add_separator()
Help.menu.add_command(label="About", command=ShowAbout)

global Default
Default=0
ChannelList=Toplevel(bg="#676760")
ChannelList.protocol("WM_DELETE_WINDOW", lambda: ChannelList.withdraw())
ChannelList.title("Channel listing for (not connected)")
Filter=Label(ChannelList, text="Filter:", bg="#676760",
         fg="#f7f7f7", font=("Courier New",12))
Filter.grid(row=0, column=1, sticky=N+W)
FilterEntry=Entry(ChannelList, bg="#9d9a95", fg="#f7f7f7", font=("Courier New",12))
FilterEntry.bind("<KeyRelease>", FilterList)
FilterEntry.grid(row=0, column=2, sticky=N+W)
Checkbox=Checkbutton(ChannelList, text="default filter", bg="#676760",
                     fg="#f7f7f7", font=("Courier New",10), selectcolor="#7f0303",
                     activebackground="#676760", activeforeground="#f7f7f7",
                     command=DefaultFilter)
Checkbox.grid(row=0, column=3, sticky=N+W)
ChanList=Listbox(ChannelList, bg="#676760", fg="#f7f7f7",
                 font=("Courier New", 12), selectforeground="#f7f7f7")
ChanList.bind("<Double-Button-1>", joinchan)
ChanList.grid(column=0, row=1, columnspan=4, sticky=N+S+E+W)
Vscroll3=Scrollbar(ChannelList, command=ChanList.yview, bg="#7f0303", troughcolor="#cc2b00")
Vscroll3.grid(column=4, row=1, sticky=N+S)
ChanList["yscrollcommand"]=Vscroll3.set
ChannelList.columnconfigure(3, weight=1)
ChannelList.rowconfigure(1, weight=1)
# UNCOMMENT THIS WINDOWS THREADING ERROR
ChannelList.withdraw()


About.mainloop()
ChannelList.mainloop()
root.mainloop()
irc.process_forever()
