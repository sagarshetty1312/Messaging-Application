import os

from message import *
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from json import JSONEncoder
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

usernames=['admin']
channelnames=['default']
messagemap={'default':[]}

@app.route("/", methods=["POST","GET"])
def index():
    """Adds username/channelname and returns homepage"""
    username = request.form.get("username")
    usernames.append(username)
    channelname = request.form.get("channelname")
    if channelname != None:
        channelnames.append(channelname)
        now = datetime.now()
        time = now.strftime("%H:%M")
        messagemap[channelname]=[]
    return render_template('index.html', username=username, channelnames=channelnames)


@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/checkusername", methods=["POST"])
def checkusername():
    username = request.form.get("username")
    for u in usernames:
        if(u == username):
            return jsonify({"availabe":False})
    return jsonify({"availabe":True})

@app.route("/createchannel")
def createchannel():
    return render_template("createchannel.html")

@app.route('/checkcname', methods=["POST"])
def checkcname():    
    cname = request.form.get("cname")
    for c in channelnames:
        if(c == cname):
            return jsonify({"availabe":False})
    return jsonify({"availabe":True})

@app.route("/channel/<string:channelname>")
def channel(channelname):
    """Opens an existing channel"""
    if channelname not in messagemap:
        return "Channel doesn't exist"
    else:
        return render_template("channel.html", channelname=channelname)

@app.route("/messages" )
def messages():
    """Returns messages for the given channel"""
    channel = request.form.get("channel")
    temp_messages = messagemap[channel]
    messages = []
    for message in temp_messages:
        messages.append(message.__dict__)
    return jsonify(messages)

@socketio.on("send message")
def newmessage(data):
    channel = data["channel"]
    message = addmessage(channel, data["sender"], data["message"])
    emit("new message", {"message": message.__dict__, "channel": channel}, broadcast = True)

@socketio.on("delete message")
def broadcastdelete(data):
    channel = data["channel"]
    id = int(data["id"])
    deletemessage(channel,id)
    emit("message deleted",{"channel":channel, "id": id}, broadcast=True)


def addmessage(channel,sender,message):
    messagelist = messagemap[channel]

    if messagelist == []:
        id = 1
    else:
        temp_message = messagelist[-1]
        id = temp_message.id + 1
    if id == 101:
        deletemessage(channel,1)
        id = id-1
    now = datetime.now()
    time = now.strftime("%H:%M")
    messageObj = Message(sender, id, message, time)
    messagelist.append(messageObj)
    return messageObj

def deletemessage(channel,id):
    messagelist = messagemap[channel]
    last_id = len(messagelist)-1
    messagelist.pop(id-1)
    if len(messagelist) > 0:
        index = id-1
        while(index < len(messagelist)):
            temp_message = messagelist[index]
            temp_message.id = temp_message.id-1
            index = index+1
    return True