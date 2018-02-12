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
        print ('---IT IS WEB SOCKET---')
        uuid = int(time.time()*1000)
        stream =json.dumps(dict({'uuid':uuid,'type':'connection'}))
        request.websocket.send(bytes(stream, encoding='UTF-8'))
        clients.append(request.websocket) #Add to clients list
        print ('---ADD A NEW SOCKET, WE HAVE {}---'.format(clients))

        for message in request.websocket:
            if not message:
                clients.remove(request.websocket)
                print ('---WE HAVE REMAININGS: {} ---`'.format(clients))
            else:
                for client in clients:
                    client.send(message)  #发送消息到客户端
                    print ('---SEND {} TO {}---'.format(message, client))



