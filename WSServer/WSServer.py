
'''
The MIT License (MIT)
Copyright (c) 2013 Dave P.
'''

import signal
import sys
import ssl
import json
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from kafka import KafkaProducer, KafkaConsumer
from datetime import datetime, date
from time import strftime
import decimal
import _thread

def json_serial(obj):
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()

  if isinstance(obj, decimal.Decimal):
    return float(obj)

  raise TypeError("Type is not serializable %s" % type(obj))

def start_listen_event():
    #upd_external_event_trigger
    consumer = KafkaConsumer('upd_external_event_trigger', group_id='my-group', bootstrap_servers=['192.168.5.131:9092'])
        
    for message in consumer:
        msgArray = json.loads(message.value)
        #print(msgArray['Данные'])
        
        for client in clients:
            tmpData = {}
            tmpData['d_ref'] = msgArray['Данные']['d_ref']
            #tmpData['date'] = msgArray['Данные']['date'].strftime("%d-%m-%Y %H:%M:%S")
            tmpData['date'] = datetime.strptime(msgArray['Данные']['date'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y 0:00:00")
            #datetime.datetime.strptime(msgArray['Данные']['date'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.%Y 0:00:00")
            #client.sendMessage(msgArray['Данные']['d_ref'])
            if tmpData['d_ref'] == client.d_ref:
                client.sendMessage(json.dumps(tmpData, default=json_serial))
 

class SimpleEcho(WebSocket):

   def handleMessage(self):
      self.sendMessage(self.data)

   def handleConnected(self):
      pass

   def handleClose(self):
      pass

clients = []
class SimpleChat(WebSocket):

   def handleMessage(self):
      #for client in clients:
      #   if client != self:
      #      client.sendMessage(self.address[0] + u' - ' + self.data)

      # update d_ref of this client
      for client in clients:
         if client == self:
             client.d_ref = self.data.upper()
             #client['d_ref'] = self.data

   def handleConnected(self):
      print ('['+datetime.now().strftime("%d-%m-%Y %H:%M:%S")+']', self.address, 'connected')
      # default
      self.d_ref = ''
      #for client in clients:
      #   client.sendMessage(self.address[0] + u' - connected')
      clients.append(self)

   def handleClose(self):
      clients.remove(self)
      print ('['+datetime.now().strftime("%d-%m-%Y %H:%M:%S")+']', self.address, 'closed')
      #for client in clients:
      #   client.sendMessage(self.address[0] + u' - disconnected')


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='0.0.0.0', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=2033, type='int', action="store", dest="port", help="port (8000)")
   parser.add_option("--example", default='chat', type='string', action="store", dest="example", help="echo, chat")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--key", default='./key.pem', type='string', action="store", dest="key", help="key (./key.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")

   (options, args) = parser.parse_args()

   cls = SimpleEcho
   if options.example == 'chat':
      cls = SimpleChat

   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.key, version=options.ver)
   else:
      server = SimpleWebSocketServer(options.host, options.port, cls)

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   # listen kafka
   _thread.start_new_thread(start_listen_event, ())
   print('Listen Kafka thread - upd_external_event_trigger')

   # listen websocket
   print('Start WebSocket server on '+str(options.host)+':'+str(options.port))
   server.serveforever()

   