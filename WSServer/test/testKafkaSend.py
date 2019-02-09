import time
import json
from datetime import datetime, date
from kafka import KafkaProducer, KafkaConsumer 

def json_serial(obj):
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()

  if isinstance(obj, decimal.Decimal):
    return float(obj)

  raise TypeError("Type is not serializable %s" % type(obj))

for x in range(1, 20):
    producer = KafkaProducer(bootstrap_servers=['192.168.5.131:9092'])
    
    d = {}
    d['Действия'] = 'External_Record_Log_Event' 
    d['Данные'] = {} 
    d['Данные']['d_ref'] = '8671001A6476004111E18E84192B6F91' 
    d['Данные']['date'] = '06.02.2019 00:00:00'
    d['event_date'] = datetime.now()

    jdata = json.dumps(d, default=json_serial)
    
    #user =''.encode('utf-8')

    key = '09ujfiweiojf'.encode('utf-8')
    value = jdata.encode('utf-8')

    producer.send(f'upd_external_event_trigger', key=key, value=value)
    time.sleep(5)
