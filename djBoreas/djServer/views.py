from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse
import time
import threading
import json

# Create your views here.

def index(request):
    return render(request, 'index.html')


clients = []
old_connected_msgs = []

def broadcast(msg):
    for client in clients:
        client.send(msg) #发送消息到客户端
        print ('---SEND {} TO {}---'.format(msg, client))


@accept_websocket
def handle_websocket(request):
    if not request.is_websocket():#判断是不是websocket连接
        print ('---IT IS NOT SOCKET---')
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request,'index.html')
    else:
        print ('---A NEW CONNECTION---')
        # A new connection
        uuid = int(time.time()*1000) #the millisecond timestamp of connected-in used as uuid
        connected_msg = bytes(json.dumps(dict({'uuid':uuid,'type':'connection','action':'connected'})), encoding='UTF-8') 
        sync_msg = bytes(json.dumps(dict({'uuid':uuid,'type':'connection','action':'sync'})), encoding='UTF-8') 
        
        # To A New Client
        request.websocket.send(connected_msg) # uuid
        for old_connected_msg in old_connected_msgs:
            request.websocket.send(old_connected_msg) # old uuid

        # To olds
        broadcast(connected_msg)  #boardcast the uuid to old clients

        # Record as an old
        old_connected_msgs.append(sync_msg) # store the id
        clients.append(request.websocket) #add the client to the list
        print ('---ADD A NEW SOCKET, WE HAVE {} NOW: {}---'.format(len(clients),clients))

        # On-going connection
        for message in request.websocket:
            if message:
                broadcast(message)
            # disconnected
            if not message:
                clients.remove(request.websocket)
                old_connected_msgs.remove(sync_msg)
                
                print ('---WE HAVE {} REMAININGS: {} ---`'.format(len(clients), clients))
                stream_msg =bytes(json.dumps(dict({'uuid':uuid,'type':'connection','action':'disconnected'})), encoding='UTF-8')
                broadcast(stream_msg)
                
                
                    



