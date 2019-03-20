from datetime import datetime
from flask import render_template, request
import json
from server import app
import requests


headers = {'Content-type': 'application/json'}
           #'Accept': 'text/plain'}

erl_url = 'http://192.168.7.220:2032'


@app.route('/get_free_timeslots')
def get_free_timeslots():
    #192.168.7.220:2034/get_free_timeslots?dep=B6B200215E2D367211DE54A0A95281DC&date=01.01.2019
    dep = request.args.get('dep', '').upper() 
    
    date = request.args.get('date', '').upper() 

    #file_name = date

    date = datetime.strptime(date, "%d-%m-%Y")
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) 

    date_str = date.strftime("%d.%m.%Y %H:%M:%S")
   
    r = requests.get(f"""{erl_url}/get?d_ref={dep}&date={date_str}""")
    
    answer = json.loads(r.text)

    advisers = {}

    for x in answer['timeline']['groups']:
        if x.get('pos_name') is None:
            continue

        if x['pos_name'] == 'Мастер-приемщик':
            advisers[x['id']] = x['content']

    time_slot = answer['timeline']['items']

    time_slot = sorted(time_slot, key=lambda e: e['start']) 
     
    t = {}
    
    t['date'] = date.strftime("%Y-%m-%d")
    t['slots'] = []
    t['advisers'] = advisers
    
    for y in time_slot:
        if advisers.get(y['group']) is None:
            continue
            
        available = True
        if y.get('type') is None:
            available = y['className'] == 'expected'
        else:
            continue

        time_delivery = False

        for z in time_slot:
            if z['group'] == y['group'] and z['start'] == y['start']:
                if not z.get('type') is None:
                    time_delivery = True

        if time_delivery == True:
            continue

        start = datetime.strptime(y['start'], "%Y-%m-%dT%H:%M:%S.%f")
        end = datetime.strptime(y['end'], "%Y-%m-%dT%H:%M:%S.%f")

        duration = (end - start).seconds

        #start = start.strftime("%H:%M:%S")
        #end = end.strftime("%H:%M:%S")

        adviser = y['group']

        tt = {'start':start, 'end':end, 'duration':duration, 'adviser':adviser, 'available':available}
        
        t['slots'].append(tt)

    res = json.dumps(t, default=json_serial)
    
    #with open(file_name, 'w') as file:
    #    file.write(res)

    return res, 200, headers

def json_serial(obj):
    from datetime import datetime, date
    import decimal
    if isinstance(obj, (datetime, date)):
       return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
       return float(obj)
    pass

