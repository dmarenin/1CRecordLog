from server.consts import *
from datetime import timedelta, datetime
import uuid

# region service

def res_to_vis_js(data, date, dep_work_time, list_time_reserved, r_ref, is_garant, empl_dev, work_time_posts, undistributed_works):
    _time_begin = '2018-01-01 time_begin:00'.replace('time_begin', data['time_end'])
    _time_end = '2018-01-02 time_end:00'.replace('time_end', data['time_begin'])

    data['timeline'] = {}
    
    data['timeline']['hiddenDates'] = [{ 'start': _time_begin, 'end': _time_end, 'repeat': 'daily' }]
    
    timeline = data['timeline']

    timeline['groups'] = []    
    
    timeline['items'] = []
    timeline['items_unselected'] = []
    timeline['items_garant'] = []
    timeline['links'] = {}

    time_acceptions = data['time_acceptions']

    time_accept_step = (int)(time_acceptions / TIME_STEP)

    empls = data['empl']
    eqips = data['eqip']

    #region empl

    order = 0
    val = 0 
    for x in empls:
        val += 1
        order +=1

        empl = empls.get(x)

        className = 'openwheel'

        style = "background-color: white;"

        if empl['pos_name'] == POS_NAME_MP:
            style = "color: white; background-color: grey;"

        str_empl_dev = ''
        if not empl_dev is None:
            for y in empl_dev:
                if y['employee'] == x:
                    str_empl_dev = ' (' + str(round(y['count'], 1)) + ' ч)'

        content = (empl['m_name'] + '<BR>' + str(empl['pos_name'])) + str_empl_dev,

        d = {'content':str(content[0]), 'id':empl['m_ref'], 'value':val, 'className': className, 'style': style, 'order':order}

        timeline['groups'].append(d)

        work_time_empl = dep_work_time.get(x)

        wt_start_accept = None
        _wt_start_accept = []

        if not work_time_empl is None:
            _wt_start_accept = []

            for wt_l in work_time_empl['lunch_time']:
                wt_l_date_end = wt_l['period_date_time'] + timedelta(minutes=TIME_STEP)

                style = 'color: red; background-color: #CCCCCC;' 
                
                d3 = {'start' : wt_l['period_date_time'].strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :   wt_l_date_end.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '', 'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}

                timeline['items'].append(d3)
                timeline['items_unselected'].append(d3)
                timeline['items_garant'].append(d3)
               
            for wt_n in work_time_empl['not_working_time']:
                wt_l_date_end = wt_n['period_date_time'] + timedelta(minutes=TIME_STEP)

                style = 'color: red; background-color: #CCCCCC;' 
                
                d2 = {'start' : wt_n['period_date_time'].strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :   wt_l_date_end.strftime("%Y-%m-%dT%H:%M:00.000"),'group' : x, 'content' : '', 'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}

                timeline['items'].append(d2)
                timeline['items_unselected'].append(d2)
                timeline['items_garant'].append(d2)
                            
            for v in list_time_reserved:
                if empl['pos_name'] != POS_NAME_MP:
                    break

                wt_start_accept = []
                last_date_max = None
                for wt_w in work_time_empl['working_time']:
                   if wt_w['period_date_time'].hour < v['accept_start'].hour:
                       continue
                   if wt_w['period_date_time'].hour > v['accept_end'].hour:
                       continue

                   if last_date_max is None:
                       last_date_max = wt_w['period_date_time'] + timedelta(minutes=time_acceptions)

                       wt_start_accept.append(wt_w['period_date_time'])

                       if not wt_w['period_date_time'] in _wt_start_accept:
                           _wt_start_accept.append(wt_w['period_date_time'])

                   if last_date_max == wt_w['period_date_time']:
                       wt_start_accept.append(wt_w['period_date_time'])
                       
                       if not wt_w['period_date_time'] in _wt_start_accept:
                            _wt_start_accept.append(wt_w['period_date_time'])

                       last_date_max = wt_w['period_date_time'] + timedelta(minutes=time_acceptions)
                   else:
                       for __x in work_time_empl['lunch_time']:
                           if __x['period_date_time'] == last_date_max:
                               last_date_max = work_time_empl['lunch_time'][len(work_time_empl['lunch_time']) - 1]['period_date_time'] + timedelta(minutes=TIME_STEP)  
                               break

                rule = {'every' : 1, 'from':1}

                if v['accept_proc'] is None:
                    continue
                elif v['accept_proc'] == 0:
                    rule = {'every' : 0, 'from':0}               
                elif v['accept_proc'] == 100:
                    rule = {'every' : 1, 'from':1}                
                elif v['accept_proc'] == 50:
                    rule = {'every' : 1, 'from':2}              
                elif v['accept_proc'] == 33:
                    rule = {'every' : 2, 'from':3}             
                elif v['accept_proc'] == 66:
                    rule = {'every' : 1, 'from':3}              
                elif v['accept_proc'] == 25:
                    rule = {'every' : 1, 'from':4}

                count = 1               
                
                for _x in wt_start_accept:
                    if count == rule['from']:
                        count = 1
                        continue

                    if count <= rule['every']:
                        style = 'color: red; background-color: #CCFFFF;'
                            
                        d4 = {'start' : _x.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : (_x + timedelta(minutes=time_acceptions)).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '',          'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}
                   
                        timeline['items'].append(d4)
                        timeline['items_unselected'].append(d4)
                        timeline['items_garant'].append(d4)

                    count += 1

        wt_accept = []

        for y in empl['periods']:
            if y['r_ref'] is None:
                continue
            
            if timeline['links'].get(y['r_ref']) is None:
                timeline['links'][y['r_ref']] = []

            id_item = y['r_ref'] + '_' + str(y['num_str'])
            start_item = y['r_begin'].strftime("%Y-%m-%dT%H:%M:00.000")
            end_item = y['r_end'].strftime("%Y-%m-%dT%H:%M:00.000")

            timeline['links'][y['r_ref']].append(id_item)

            class_name = get_class_name_from_record(y, empl, is_garant, data)
            
            content = get_content_from_record(y)

            d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}

            if not r_ref is None:
                d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'unselected', 'content' : '', 'title': content, 'editable' : False, 'id': id_item}
                
                if r_ref == y['r_ref']:
                    d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'select_ref', 'content' : str(y['c_name']),                'title': '', 'editable' : True, 'id': id_item}  

            timeline['items'].append(d)

            wt_accept.append({'r_begin' : y['r_begin'], 'r_end' : y['r_end']})

            d1 = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'unselected', 'content' : '', 'title': content, 'id': id_item}

            timeline['items_unselected'].append(d1)
          
            class_name = get_class_name_from_record(y, empl, True, data)
            
            d2 = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}

            timeline['items_garant'].append(d2)

        wt_accept = res = sorted(wt_accept, key=lambda e: e['r_begin'], reverse=False)

        if empl['pos_name'] == POS_NAME_MP:
            if not _wt_start_accept is None:
                for _y in wt_accept:
                    for _x in reversed(_wt_start_accept): 
                        _x_end = _x + timedelta(minutes=time_acceptions)

                        if _y['r_begin'] == _x and _y['r_end'] == _x_end:
                            _wt_start_accept.remove(_x)
                        
                        if _y['r_begin'] == _x and _y['r_end'] < _x_end:
                            _wt_start_accept.remove(_x)
                        
                        if _y['r_begin'] == _x and _y['r_end'] > _x_end:
                            _wt_start_accept.remove(_x) 
                            
                        if _x > _y['r_begin'] and _x < _y['r_end'] :
                            _wt_start_accept.remove(_x)
                        
                        if _x < _y['r_begin'] and _x_end > _y['r_begin'] :
                            _wt_start_accept.remove(_x)

                for _x in _wt_start_accept:
                    d5 = {'start' : _x.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : (_x + timedelta(minutes=time_acceptions)).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '<BR>',          'title' : _x.strftime("%H:%M") + '-' + (_x + timedelta(minutes=time_acceptions)).strftime("%H:%M"), 'className' : 'expected', 'id' : str(uuid.uuid4())}
                   
                    timeline['items'].append(d5)


    #endregion

    #region posts

    num_day = date.weekday()+1

    time_posts_list = data['time_posts_list']
    for x in time_posts_list:
       if x['num_day'] != num_day:
           continue
       time_begin_posts = x['periodStart']
       time_end_posts = x['periodEnd']

    style = "color: white; background-color: #999999;"
    eq = []
    className = 'openwheel'
    order = 100

    for e in eqips:
        val += 1
        order +=1

        eqip = eqips.get(e)

        hours_in_day = (time_end_posts - time_begin_posts).seconds / 3600

        total_hours = 0

        for y in eqip['periods']:
            total_hours += (y['r_end'] - y['r_begin']).seconds / 3600

        perc = (total_hours / hours_in_day) * 100

        perc = int(perc)

        progres_style = "progress"
        if perc > 50:
           progres_style = "progress3"
            
           if perc <= 85:
               progres_style = "progress2"

        progres_style = f"""<div class="progress-wrapper"><div class="{progres_style}" style="width:{str(perc)}%"></div><label class="progress-label">{str(perc)} %<label></div>"""

        content = eqip['eq_name'] + '<BR>' + progres_style

        d = {'content':str(content), 'id':eqip['eq_ref'], 'value':val, 'className': className, 'style': style, 'order':order}

        timeline['groups'].append(d)

        eq.append(eqip['eq_ref'])

        for y in eqip['periods']:
            if y['r_ref'] is None:
                continue
            
            if timeline['links'].get(y['r_ref']) is None:
                timeline['links'][y['r_ref']] = []

            id_item = y['r_ref'] + '_' + str(y['num_str'])           
            start_item = y['r_begin'].strftime("%Y-%m-%dT%H:%M:00.000")
            end_item = y['r_end'].strftime("%Y-%m-%dT%H:%M:00.000")

            timeline['links'][y['r_ref']].append(id_item)

            class_name = get_class_name_from_record(y, eqip, is_garant, data)
            
            content = get_content_from_record(y)

            if r_ref is None:
                 d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}
            
            else:
                d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : 'unselected', 'content' : '', 'title': content,
                 'editable' : False, 'id': id_item}
                
                if r_ref == y['r_ref']:
                    d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : 'select_ref', 'content' : str(y['c_name']),                'title': '', 'editable' : True, 'id': id_item}  

            timeline['items'].append(d)

            wt_accept.append({'r_begin' : y['r_begin'], 'r_end' : y['r_end']})

            d1 = {'start' : start_item, 'end' :  end_item, 'group' : e, 'className' : 'unselected', 'content' : '', 'title': content, 'id': id_item}

            timeline['items_unselected'].append(d1)
          
            class_name = get_class_name_from_record(y, empl, True, data)
            
            d2 = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}

            timeline['items_garant'].append(d2)

    content = 'Посты <BR> <BR>' 
        
    class_name = 'expected'

    for p in work_time_posts:

        if not p['val_char'] in eq:
            order += 1
            timeline['groups'].append({'id':p['val_char'], 'content': p['post_name'] + '<BR>' + '<div class="progress-wrapper"><div class="progress" style="width:0%"></div><label class="progress-label"><label></div>', 'order':order, 'style':style})

            eq.append(p['val_char'])
        
        __date_start = date + timedelta(hours=int(data['time_begin'][0:2]))
        __date_stop = date + timedelta(days=1) 

        #date_start = date + timedelta(hours=int(data['time_begin'][0:2]))
        #date_stop = date + timedelta(days=1) 

        date_start = date.replace(hour=time_begin_posts.hour, minute=time_begin_posts.minute, second=0, microsecond=0)  
        date_stop = date.replace(hour=time_end_posts.hour, minute=time_end_posts.minute, second=0, microsecond=0)   

        d2 = {'start' : __date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['val_char'], 'type' : 'background',    'content' : '', 'title' : '', 'style' : 'color: red; background-color: #CCCCCC;' ,  'id': str(uuid.uuid1(),)}
        
        timeline['items'].append(d2)
        timeline['items_unselected'].append(d2)
        timeline['items_garant'].append(d2) 

        d2 = {'start' : date_stop.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : __date_stop.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['val_char'], 'type' : 'background',    'content' : '', 'title' : '', 'style' : 'color: red; background-color: #CCCCCC;' ,  'id': str(uuid.uuid1(),)}
        timeline['items'].append(d2)
        timeline['items_unselected'].append(d2)
        timeline['items_garant'].append(d2) 

        style1 = None
  
        periods = []

        if not eqips.get(p['val_char']) is None:
            for c in eqips.get(p['val_char'])['periods']:
                periods.append({'r_begin':c['r_begin'], 'r_end': c['r_end']})

        periods = sorted(periods, key=lambda e: e['r_begin'])

        while date_start < date_stop:
            if len(periods)==0:
                d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=p['val_int'])).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['val_char'], 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=p['val_int'])).strftime("%H:%M"), 'style' : style1, 'className' : class_name, 'id': str(uuid.uuid1(),)}
       
                timeline['items'].append(d5)

            else:
                is_exist = False

                for pw in periods:
                    _x_end = date_start + timedelta(minutes=p['val_int'])

                    if pw['r_begin'] == date_start and pw['r_end'] == _x_end:
                        is_exist = True
                        break
                        
                    if pw['r_begin'] == date_start and pw['r_end'] < _x_end:
                        is_exist = True
                        break
                        
                    if pw['r_begin'] == date_start and pw['r_end'] > _x_end:
                        is_exist = True
                        break
                            
                    if date_start > pw['r_begin'] and date_start < pw['r_end'] :
                        is_exist = True
                        break
                       
                    if date_start < pw['r_begin'] and _x_end > pw['r_begin'] :
                        is_exist = True
                        break

                if not is_exist:
                    d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=p['val_int'])).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['val_char'], 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=p['val_int'])).strftime("%H:%M"), 'style' : style1, 'className' : class_name, 'id': str(uuid.uuid1(),)}
       
                    timeline['items'].append(d5)

            date_start = date_start + timedelta(minutes=p['val_int'])


    d = {'content':content, 'id':str(uuid.uuid1()),  'className': className, 'style': style, 'nestedGroups':eq, 'showNested': True, 'order':order}
        
    timeline['groups'].append(d)

    #endregion

    #region undistributed_works

    if not r_ref is None:
        if not undistributed_works is None:
            for x in undistributed_works:
                if x!=r_ref:
                    continue
                if len(undistributed_works.get(x))>0:
                    timeline['works'] = []
                    for y in undistributed_works.get(x):
                        #timeline['works'].append({'name': f""" {y['service_name']} ({round(y['work_hour']*y['amount'] ,2)} ч)""", 'service':y['service'], 'ref':y['ref'], 'num_str':y['num_str'], 'amount':y['work_hour']*y['amount']})
                        timeline['works'].append({'name': f""" {y['service_name']} ({round(y['hours_total'],2)} ч)""", 'service':y['service'], 'ref':y['ref'], 'num_str':y['num_str'], 'amount':y['hours_total']})

                        

    #endregion
    
    return data

def get_content_from_record(data):
    str_car = str(data['car_name'])
    
    if data['car_name'] is None:
        str_car = str(data['carStr'])

    content = f"""С {data['r_begin'].strftime('%H:%M')} по {data['r_end'].strftime('%H:%M')}
<BR>Заказчик: {str(data['c_name'])}
<BR>Контрагент: {str(data['k_name'])}
<BR>Автомобиль: {str_car} ({str(data['carNumber'])})
<BR><B>Причина обращения: {str(data['reason'])}</B>
<BR>Вид ремонта: {str(data['kind_repair_name'])}
<BR>Автор: {str(data['user_name'])}"""

    return content

def get_class_name_from_record(i, empl, is_garant, res):
    class_name = 'empty' 

    if is_garant == True:       
        class_name = 'not_is_guarantee'
       
        if i['is_guarantee'] == 1:          
            class_name = 'is_guarantee'

    else:
        class_name = 'empty'
                
        if i['type'] == 'order':
             class_name = 'order'
        elif i['type'] == 'closed':
              class_name = 'closed'            
        elif i['type'] == 'query':
             class_name = 'query'
        elif i['type'] == 'record' and not i['z_ref'] is None:
              class_name = 'record_having_zn' 

        if i['is_guarantee'] == 1 and (i['z_ref'] is None or i['q_ref'] is None):
              class_name = 'not_is_guarantee_not_having_zn'
     
        if i['type'] == 'record' and i['z_ref'] is None and i['q_ref'] is None and empl.get('pos_name') == POS_NAME_MP: 
             var_b = False
                
             for var_x in res['empl']:

                if res['empl'].get(var_x)['pos_name'] == POS_NAME_MP:
                     continue
                   
                for var_i in res['empl'].get(var_x)['periods']:                    
                     if i['r_ref_ones'] == var_i['r_ref_ones']:
                            
                         var_b = True
                         break
                        
             if var_b != True:
                 class_name = 'not_assigned_empl' 

        if i['kind_work_ref'] == '9578CE73-8573-43BD-9E7C-CFFD60C2AC91':
            class_name = 'is_delivery' 

    return class_name

# endregion

# region sale

def res_to_vis_js_test_drive(data, date, r_ref, dep_work_time):
    _time_begin = '2018-01-01 time_begin:00'.replace('time_begin', data['time_end'])
    _time_end = '2018-01-02 time_end:00'.replace('time_end', data['time_begin'])

    data['timeline'] = {}
    
    data['timeline']['hiddenDates'] = [{ 'start': _time_begin, 'end': _time_end, 'repeat': 'daily' }]
    
    timeline = data['timeline']

    timeline['groups'] = []    
    
    timeline['items'] = []
    timeline['items_unselected'] = []

    timeline['links'] = {}

    work_time_posts = data['work_time_posts']

    #TIME_TEST_DRIVE

    #time_acceptions = data['time_acceptions']

    #time_accept_step = (int)(time_acceptions / TIME_STEP)

    empls = data['empl']
    eqips = data['eqip']

    #region empl

    order = 0
    val = 0 
    for x in empls:
        empl = empls.get(x)
        if empl['m_ref'] is None:
            continue

        val += 1
        order +=1

        className = 'openwheel'

        style = "background-color: white;"

        #if empl['pos_name'] == POS_NAME_MP:
        style = "color: white; background-color: grey;"

        content = (empl['m_name'] + '<BR>' + str(empl['pos_name']))

        d = {'content':str(content), 'id':empl['m_ref'], 'value':val, 'className': className, 'style': style, 'order':order}

        timeline['groups'].append(d)

        work_time_empl = dep_work_time.get(x)

        wt_start_accept = None
        _wt_start_accept = []

        if not work_time_empl is None:
            _wt_start_accept = []

            for wt_l in work_time_empl['lunch_time']:
                wt_l_date_end = wt_l['period_date_time'] + timedelta(minutes=TIME_STEP)

                style = 'color: red; background-color: #CCCCCC;' 
                
                d3 = {'start' : wt_l['period_date_time'].strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :   wt_l_date_end.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '', 'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}

                timeline['items'].append(d3)
                timeline['items_unselected'].append(d3)
               
            for wt_n in work_time_empl['not_working_time']:
                wt_l_date_end = wt_n['period_date_time'] + timedelta(minutes=TIME_STEP)

                style = 'color: red; background-color: #CCCCCC;' 
                
                d2 = {'start' : wt_n['period_date_time'].strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :   wt_l_date_end.strftime("%Y-%m-%dT%H:%M:00.000"),'group' : x, 'content' : '', 'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}

                timeline['items'].append(d2)
                timeline['items_unselected'].append(d2)
                            
        #   for v in list_time_reserved:
        #        if empl['pos_name'] != POS_NAME_MP:
        #            break

        #        wt_start_accept = []
        #        last_date_max = None
        #        for wt_w in work_time_empl['working_time']:
        #           if wt_w['period_date_time'].hour < v['accept_start'].hour:
        #               continue
        #           if wt_w['period_date_time'].hour > v['accept_end'].hour:
        #               continue

        #           if last_date_max is None:
        #               last_date_max = wt_w['period_date_time'] + timedelta(minutes=time_acceptions)

        #               wt_start_accept.append(wt_w['period_date_time'])

        #               if not wt_w['period_date_time'] in _wt_start_accept:
        #                   _wt_start_accept.append(wt_w['period_date_time'])

        #           if last_date_max == wt_w['period_date_time']:
        #               wt_start_accept.append(wt_w['period_date_time'])
                       
        #               if not wt_w['period_date_time'] in _wt_start_accept:
        #                    _wt_start_accept.append(wt_w['period_date_time'])

        #               last_date_max = wt_w['period_date_time'] + timedelta(minutes=time_acceptions)
        #           else:
        #               for __x in work_time_empl['lunch_time']:
        #                   if __x['period_date_time'] == last_date_max:
        #                       last_date_max = work_time_empl['lunch_time'][len(work_time_empl['lunch_time']) - 1]['period_date_time'] + timedelta(minutes=TIME_STEP)  
        #                       break

        #        rule = {'every' : 1, 'from':1}

        #        if v['accept_proc'] is None:
        #            continue
        #        elif v['accept_proc'] == 0:
        #            rule = {'every' : 0, 'from':0}               
        #        elif v['accept_proc'] == 100:
        #            rule = {'every' : 1, 'from':1}                
        #        elif v['accept_proc'] == 50:
        #            rule = {'every' : 1, 'from':2}              
        #        elif v['accept_proc'] == 33:
        #            rule = {'every' : 2, 'from':3}             
        #        elif v['accept_proc'] == 66:
        #            rule = {'every' : 1, 'from':3}              
        #        elif v['accept_proc'] == 25:
        #            rule = {'every' : 1, 'from':4}

        #        count = 1               
                
        #        for _x in wt_start_accept:
        #            if count == rule['from']:
        #                count = 1
        #                continue

        #            if count <= rule['every']:
        #                style = 'color: red; background-color: #CCFFFF;'
                            
        #                d4 = {'start' : _x.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : (_x + timedelta(minutes=time_acceptions)).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '',          'title' : '', 'id' : str(uuid.uuid4()), 'type' : 'background', 'style' : style}
                   
        #                timeline['items'].append(d4)
        #                timeline['items_unselected'].append(d4)
        #                timeline['items_garant'].append(d4)

        #            count += 1

        #wt_accept = []
                
        for y in empl['periods']:
            if y['r_ref'] is None:
                continue
            
            if timeline['links'].get(y['r_ref']) is None:
                timeline['links'][y['r_ref']] = []

            id_item = y['r_ref'] + '_' + str(order)
            start_item = y['r_begin'].strftime("%Y-%m-%dT%H:%M:00.000")
            end_item = y['r_end'].strftime("%Y-%m-%dT%H:%M:00.000")

            timeline['links'][y['r_ref']].append(id_item)

            class_name = 'empty'
                
            if y['r_post'] == True:
                class_name = 'order'
                    
            content = f"""С {y['r_begin'].strftime('%H:%M')} по {y['r_end'].strftime('%H:%M')}
<BR>Заказчик: {str(y['c_name'])}
<BR>Автомобиль: {str(y['car_name'])}
<BR><B>Причина обращения: {y['reason']} </B>
<BR>Автор: {str(y['user_name'])}"""

            d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}

            if not r_ref is None:
                d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'unselected', 'content' : '', 'title': content, 'editable' : False, 'id': id_item}
                
                if r_ref == y['r_ref']:
                    d = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'select_ref', 'content' : str(y['c_name']), 'title': '', 'editable' : True, 'id': id_item}  

            timeline['items'].append(d)

            d1 = {'start' : start_item, 'end' : end_item, 'group' : x, 'className' : 'unselected', 'content' : '', 'title': content, 'id': id_item}

            timeline['items_unselected'].append(d1)

        date_start = date.replace(hour=int(data['time_begin'][0:2]), minute=int(data['time_begin'][3:5]), second=0, microsecond=0)  
        date_stop = date.replace(hour=int(data['time_end'][0:2]), minute=int(data['time_end'][3:5]), second=0, microsecond=0)  

        if not work_time_empl is None and len(work_time_empl['working_time']) != 0:
            list_wt = sorted(work_time_empl['working_time'], key=lambda e: e['period_date_time'])
            
            date_start = list_wt[0]['period_date_time']
            
            list_wt = sorted(work_time_empl['working_time'], key=lambda e: e['period_date_time'], reverse=True)
            date_stop = list_wt[0]['period_date_time'] + timedelta(minutes=TIME_STEP)

        class_name = 'expected'
        while date_start < date_stop:

            if len(empl['periods'])==0:
                d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=TIME_TEST_DRIVE)).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=TIME_TEST_DRIVE)).strftime("%H:%M"), 'style' : None, 'className' : class_name, 'id': str(uuid.uuid1(),)}
                
                timeline['items'].append(d5)

            else:
                is_exist = False

                for pw in empl['periods']:
                    _x_end = date_start + timedelta(minutes=TIME_TEST_DRIVE)

                    if pw['r_begin'] == date_start and pw['r_end'] == _x_end:
                        is_exist = True
                        break
                        
                    if pw['r_begin'] == date_start and pw['r_end'] < _x_end:
                        is_exist = True
                        break
                       
                    if pw['r_begin'] == date_start and pw['r_end'] > _x_end:
                        is_exist = True
                        break
                           
                    if date_start > pw['r_begin'] and date_start < pw['r_end'] :
                        is_exist = True
                        break
                      
                    if date_start < pw['r_begin'] and _x_end > pw['r_begin'] :
                        is_exist = True
                        break
                    
                    if not is_exist:
                        d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=TIME_TEST_DRIVE)).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : x, 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=TIME_TEST_DRIVE)).strftime("%H:%M"), 'style' : None, 'className' : class_name, 'id': str(uuid.uuid1(),)}
       
                        timeline['items'].append(d5)

            date_start = date_start + timedelta(minutes=TIME_TEST_DRIVE)

    #endregion

    #region posts

    num_day = date.weekday()+1

    time_posts_list = data['time_posts_list']
    for x in time_posts_list:
       if x['num_day'] != num_day:
           continue
       time_begin_posts = x['periodStart']
       time_end_posts = x['periodEnd']

    style = "color: white; background-color: #999999;"
    eq = []
    className = 'openwheel'
    
    class_name = 'expected'
    
    order = 100

    for e in eqips:
        val += 1
        order +=1

        eqip = eqips.get(e)

        #hours_in_day = (time_end_posts - time_begin_posts).seconds / 3600
        hours_in_day = 10

        total_hours = 0

        for y in eqip['periods']:
            total_hours += (y['r_end'] - y['r_begin']).seconds / 3600

        perc = (total_hours / hours_in_day) * 100

        perc = int(perc)

        progres_style = "progress"
        if perc > 50:
           progres_style = "progress3"
            
           if perc <= 85:
               progres_style = "progress2"

           pass

        progres_style = f"""<div class="progress-wrapper"><div class="{progres_style}" style="width:{str(perc)}%"></div><label class="progress-label">{str(perc)} %<label></div>"""

        content = eqip['eq_name'] + '<BR>' + progres_style

        d = {'content':str(content), 'id':eqip['eq_ref'], 'value':val, 'className': className, 'style': style, 'order':order}

        timeline['groups'].append(d)

        eq.append(eqip['eq_ref'])

        for y in eqip['periods']:
            if y['r_ref'] is None:
                continue
            
            if timeline['links'].get(y['r_ref']) is None:
                timeline['links'][y['r_ref']] = []

            id_item = y['r_ref'] + '_' + str(order)           
            start_item = y['r_begin'].strftime("%Y-%m-%dT%H:%M:00.000")
            end_item = y['r_end'].strftime("%Y-%m-%dT%H:%M:00.000")

            timeline['links'][y['r_ref']].append(id_item)

            class_name = 'empty'
            
            content = f"""С {y['r_begin'].strftime('%H:%M')} по {y['r_end'].strftime('%H:%M')}
<BR>Заказчик: {str(y['c_name'])}
<BR>Автомобиль: {str(y['car_name'])}
<BR><B>Причина обращения: {y['reason']} </B>
<BR>Автор: {str(y['user_name'])}"""
            if y['r_post'] == True:
                class_name = 'order'

            var_b = False
                
            for var_x in empls:
                for var_i in empls.get(var_x)['periods']: 
                    if var_i['m_ref'] is None:
                        continue

                    if y['r_ref_ones'] == var_i['r_ref_ones']:
                        var_b = True
                        break
                       
            if var_b != True:
                class_name = 'not_assigned_empl' 

            elif y['r_post'] == True:
                class_name = 'order'

            if r_ref is None:
                 d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : class_name, 'content' : str(y['c_name']), 'title': content, 'id': id_item}
            
            else:
                d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : 'unselected', 'content' : '', 'title': content,
                 'editable' : False, 'id': id_item}
                
                if r_ref == y['r_ref']:
                    d = {'start' : start_item, 'end' : end_item, 'group' : e, 'className' : 'select_ref', 'content' : str(y['c_name']),                'title': '', 'editable' : True, 'id': id_item}  
                    pass

            timeline['items'].append(d)

            d1 = {'start' : start_item, 'end' :  end_item, 'group' : e, 'className' : 'unselected', 'content' : '', 'title': content, 'id': id_item}

            timeline['items_unselected'].append(d1)

    class_name = 'expected'

    for p in work_time_posts:

        if not p['car'] in eq:
            order += 1
            timeline['groups'].append({'id':p['car'], 'content': p['car_name'] + '<BR>' + '<div class="progress-wrapper"><div class="progress" style="width:0%"></div><label class="progress-label"><label></div>', 'order':order, 'style':style})

        eq.append(p['car'])
        
        __date_start = date + timedelta(hours=int(data['time_begin'][0:2]))
        __date_stop = date + timedelta(days=1) 

        date_start = date.replace(hour=time_begin_posts.hour, minute=time_begin_posts.minute, second=0, microsecond=0)  
        date_stop = date.replace(hour=time_end_posts.hour, minute=time_end_posts.minute, second=0, microsecond=0)   

        d2 = {'start' : __date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['car'], 'type' : 'background',    'content' : '', 'title' : '', 'style' : 'color: red; background-color: #CCCCCC;' ,  'id': str(uuid.uuid1(),)}
        
        timeline['items'].append(d2)
        timeline['items_unselected'].append(d2)

        d2 = {'start' : date_stop.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' : __date_stop.strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['car'], 'type' : 'background',    'content' : '', 'title' : '', 'style' : 'color: red; background-color: #CCCCCC;' ,  'id': str(uuid.uuid1(),)}
        
        timeline['items'].append(d2)
        timeline['items_unselected'].append(d2)

        style1 = None
  
        periods = []

        if not eqips.get(p['car']) is None:
            for c in eqips.get(p['car'])['periods']:
                periods.append({'r_begin':c['r_begin'], 'r_end': c['r_end']})

        periods = sorted(periods, key=lambda e: e['r_begin'])

        while date_start < date_stop:
            if len(periods)==0:
                d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=p['val_int'])).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['car'], 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=p['val_int'])).strftime("%H:%M"), 'style' : style1, 'className' : class_name, 'id': str(uuid.uuid1(),)}
       
                timeline['items'].append(d5)

            else:
                is_exist = False

                for pw in periods:
                    _x_end = date_start + timedelta(minutes=p['val_int'])

                    if pw['r_begin'] == date_start and pw['r_end'] == _x_end:
                        is_exist = True
                        break
                        
                    if pw['r_begin'] == date_start and pw['r_end'] < _x_end:
                        is_exist = True
                        break
                       
                    if pw['r_begin'] == date_start and pw['r_end'] > _x_end:
                        is_exist = True
                        break
                            
                    if date_start > pw['r_begin'] and date_start < pw['r_end'] :
                        is_exist = True
                        break
                       
                    if date_start < pw['r_begin'] and _x_end > pw['r_begin'] :
                        is_exist = True
                        break

                if not is_exist:
                    d5 = {'start' : date_start.strftime("%Y-%m-%dT%H:%M:00.000"), 'end' :  (date_start + timedelta(minutes=p['val_int'])).strftime("%Y-%m-%dT%H:%M:00.000"), 'group' : p['car'], 'content' : '<BR>','title' : date_start.strftime("%H:%M") + '-' + (date_start + timedelta(minutes=p['val_int'])).strftime("%H:%M"), 'style' : style1, 'className' : class_name, 'id': str(uuid.uuid1(),)}
       
                    timeline['items'].append(d5)

            date_start = date_start + timedelta(minutes=p['val_int'])

    content = 'Автомобили <BR> <BR>' 
        
    class_name = 'expected'

    d = {'content':content, 'id':str(uuid.uuid1()),  'className': className, 'style': style, 'nestedGroups':eq, 'showNested': True, 'order':order}
        
    timeline['groups'].append(d)

    #endregion

    return data

# endregion
