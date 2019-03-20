import time
import _thread
from kafka import KafkaProducer
from server import CACHE, CACHE_DEP, EMPL_DEV, WORK_TIME, UNDISTRIDUTED_WORKS
import json
from datetime import datetime
from server.consts import *
import orm.models as orm 
import pymssql
import peewee
from playhouse.shortcuts import case
from datetime import timedelta
import base64
from server.conf import SQL_HOST, SQL_BASE, SQL_USER, SQL_PASS, SQL_BASE_EX_W_H_DEFAULT, SQL_HOST_EX_W_H_DEFAULT, SQL_USER_EX_W_H_DEFAULT, SQL_PASS_EX_W_H_DEFAULT, SQL_BASE_EX_W_H_DEFAULT

PRODUCER = KafkaProducer(bootstrap_servers=['192.168.5.131:9092'])

UPD_EVENT_LIST = []

UPD_EVENT_LIST.append([])
UPD_EVENT_LIST.append([])
UPD_EVENT_LIST.append([])
UPD_EVENT_LIST.append([])

# region upd_loop

def upd_start():
    for i, val in enumerate(UPD_EVENT_LIST):
        _thread.start_new_thread(upd_loop, (i,))

def upd_loop(ind_upd_list):
    while True:
        do_upd_loop(ind_upd_list)

def do_upd_loop(ind_upd_list):
    t_loop = 0.150
    for x in UPD_EVENT_LIST[ind_upd_list]:
        d_ref = x['d_ref']
        date = x['date']
        type = x['type']
        
        UPD_EVENT_LIST[ind_upd_list].remove(x)
        
        if type == 0:
            if CACHE.get(d_ref) is None:
                continue
            else:
                CACHE[d_ref][date] = None 
            
            if not UNDISTRIDUTED_WORKS.get(d_ref) is None:
                UNDISTRIDUTED_WORKS[d_ref] = None

            try:
                get(d_ref, date)
            except:
                pass
            
        d = {'Действия':'External_Record_Log_Event', 'event_date':datetime.now(), 'Данные':{}}
                    
        d['Данные']['d_ref'] = d_ref 
        d['Данные']['date'] = date

        jdata = json.dumps(d, default=json_serial)

        key = d_ref.encode('utf-8')
        value = jdata.encode('utf-8')
                        
        try:
            PRODUCER.send(f'upd_external_event_trigger', key=key, value=value)
        except:
            print(f"""send to kafka failed {jdata}""")

    time.sleep(t_loop)

def add_to_upd_event_list(d_ref, date, type):
    lens = []
    
    for i, val in enumerate(UPD_EVENT_LIST):
        lens.append((len(UPD_EVENT_LIST[i]), i))

        min_list = min(lens)

    UPD_EVENT_LIST[min_list[1]].append({'d_ref':d_ref, 'date':date, 'type':type})

# endregion

# region data

def get(d_ref=None, date=None, r_ref=None, is_garant=None):
    if d_ref is None:
        return []
    
    if date is None:
        return []

    if CACHE_DEP.get(d_ref) is None:
        time_begin = get_time_begin(d_ref)
        time_end = get_time_end(d_ref)

        time_begin_posts = date.replace(hour=9, minute=0, second=0, microsecond=0) 
        time_end_posts = date.replace(hour=20, minute=0, second=0, microsecond=0) 

        time_posts_list = []

        _time_posts_list = get_setting_record_log(d_ref, WORK_DEPARTMENT_CHAR)

        if len(_time_posts_list) == 0:
            for x in range(1, 7):
                t_post = {}
                t_post['num_day'] = x
                t_post['periodStart'] = time_begin_posts
                t_post['periodEnd'] = time_end_posts

                time_posts_list.append(t_post)
        else:
            for x in _time_posts_list:
                t_post = {}
                t_post['num_day'] = x['num_day']
                t_post['periodStart'] = x['periodStart']
                t_post['periodEnd'] = x['periodEnd']

                time_posts_list.append(t_post)

        list_time_reserved = get_setting_record_log(d_ref, TIME_RESERVED_CHAR)
            
        time_acceptions = get_setting_record_log(d_ref, TIME_ACCEPTIONS_CHAR)
            
        work_time_posts = get_setting_record_log(d_ref, WORK_TIME_POSTS_CHAR)

        for p in work_time_posts:               
            post_name = orm.WorkshopEquipment.get(orm.WorkshopEquipment.ref == p['val_char']).name
    
            p['post_name'] = post_name
            
        if len(time_acceptions) == 1:
            time_acceptions = time_acceptions[0]['val_int']           
        else:   
            time_acceptions = get_time_acceptions(d_ref)

        CACHE_DEP[d_ref] = {'time_end' : time_end, 'time_acceptions' : time_acceptions, 'time_begin' : time_begin, 'list_time_reserved' : list_time_reserved, 'work_time_posts':work_time_posts, 'time_posts_list':time_posts_list}

    time_acceptions = CACHE_DEP.get(d_ref)['time_acceptions']        
    time_begin = CACHE_DEP.get(d_ref)['time_begin']      
    time_end = CACHE_DEP.get(d_ref)['time_end']
    list_time_reserved = CACHE_DEP.get(d_ref)['list_time_reserved']
    work_time_posts = CACHE_DEP.get(d_ref)['work_time_posts']
    time_posts_list = CACHE_DEP.get(d_ref)['time_posts_list'] 

    if EMPL_DEV.get(d_ref) is None:
        EMPL_DEV[d_ref] = get_empl_dev(d_ref, date) 

    if WORK_TIME.get(d_ref) is None:
        WORK_TIME[d_ref] = {}

    if not date is None:
        dep_work_time = WORK_TIME[d_ref]
        
        if dep_work_time.get(date) is None:
            dep_work_time = get_dep_work_time(d_ref, date)

            WORK_TIME[d_ref].update({date : dep_work_time})

    if CACHE.get(d_ref) is None:
        CACHE[d_ref] = {}

    cache_dep = CACHE.get(d_ref)
    
    if cache_dep.get(date) is None:
        res = get_data(d_ref, date, UNDISTRIDUTED_WORKS)
        
        res['time_acceptions'] = time_acceptions
        res['time_begin'] = time_begin
        res['time_end'] = time_end
        res['time_posts_list'] = time_posts_list

        if not CACHE.get(d_ref) is None:
            CACHE[d_ref][date] = res 
            
    else:
        res = cache_dep.get(date)   

    return res

def get_test_drive(d_ref=None, date=None):
    if d_ref is None:
        return []
    
    if date is None:
        return []

    if CACHE_DEP.get(d_ref) is None:
        time_begin = get_time_begin(d_ref)
        time_end = get_time_end(d_ref)

        time_begin_posts = date.replace(hour=9, minute=0, second=0, microsecond=0) 
        time_end_posts = date.replace(hour=20, minute=0, second=0, microsecond=0) 

        time_posts_list = []

        _time_posts_list = get_setting_record_log(d_ref, WORK_DEPARTMENT_CHAR)

        if len(_time_posts_list) == 0:
            for x in range(1, 7):
                t_post = {}
                t_post['num_day'] = x
                t_post['periodStart'] = time_begin_posts
                t_post['periodEnd'] = time_end_posts

                time_posts_list.append(t_post)
        else:
            for x in _time_posts_list:
                t_post = {}
                t_post['num_day'] = x['num_day']
                t_post['periodStart'] = x['periodStart']
                t_post['periodEnd'] = x['periodEnd']

                time_posts_list.append(t_post)

        work_time_posts = get_setting_record_log(d_ref, WORK_TIME_POSTS_CHAR)
        
        for p in work_time_posts:
            post = orm.WorkshopEquipment.get(orm.WorkshopEquipment.ref == p['val_char'])

            post_name = post.name
    
            p['post_name'] = post_name
            p['car'] = post.Значение

            if not post.Значение is None:        
                car = orm.Cars.get(orm.Cars.ref == post.Значение)
                p['car_name'] = car.name

        CACHE_DEP[d_ref] = {'work_time_posts':work_time_posts, 'time_posts_list':time_posts_list}

    if WORK_TIME.get(d_ref) is None:
        WORK_TIME[d_ref] = {}

    if not date is None:
        dep_work_time = WORK_TIME[d_ref]
        
    if dep_work_time.get(date) is None:
        dep_work_time = get_dep_work_time(d_ref, date)

        WORK_TIME[d_ref].update({date : dep_work_time})

    res = get_data_test_drive(d_ref, date)
    
    work_time_posts = CACHE_DEP.get(d_ref)['work_time_posts']
    time_posts_list = CACHE_DEP.get(d_ref)['time_posts_list']

    res['work_time_posts'] = work_time_posts
    res['time_begin'] = TIME_BEGIN
    res['time_end'] = TIME_END
    res['time_posts_list'] = time_posts_list

    return res

# endregion

# region event_upd_records

def event_upd_record_service(r_ref):
    r = (orm.RecordToLogRecord
                .select(
                    orm.RecordToLogRecord.mark.alias('mark'),
                    orm.RecordToLogRecord.posted.alias('post'),
                    orm.RecordToLogRecord.ref.alias('ref'),
                    orm.RecordToLogRecord.ref_ones.alias('ref_ones'),
                    orm.RecordToLogRecord.notCome,
                    orm.RecordToLogRecord.num_ext,
                    orm.RecordToLogRecord.dep,)
                .where(orm.RecordToLogRecord.ref == r_ref))   
                
    res = list(r.dicts())
    if len(res) == 0:
        return

    res = res[0]

    jdata = json.dumps(res, default=json_serial)

    key = res['dep'].encode('utf-8')
    value = jdata.encode('utf-8')
                        
    try:
        PRODUCER.send(f'event_upd_record_service', key=key, value=value)
    except:
        print(f"""send to kafka failed {jdata}""")

    pass

def event_upd_record_test_drive(r_ref):
    r = (orm.CRM_TestDrive
                .select(orm.CRM_TestDrive.mark.alias('mark'),
                    orm.CRM_TestDrive.posted.alias('post'),
                    orm.CRM_TestDrive.ref.alias('ref'),
                    orm.CRM_TestDrive.ref_ones.alias('ref_ones'),
                    orm.CRM_TestDrive.notCome,
                    orm.CRM_TestDrive.num_ext,
                    orm.CRM_TestDrive.dep,)           
                .where(orm.CRM_TestDrive.ref == r_ref))   

    res = list(r.dicts())
    if len(res) == 0:
        return

    res = res[0]

    jdata = json.dumps(res, default=json_serial)

    key = res['dep'].encode('utf-8')
    value = jdata.encode('utf-8')
                        
    try:
        PRODUCER.send(f'event_upd_record_test_drive', key=key, value=value)
    except:
        print(f"""send to kafka failed {jdata}""")

    pass

# endregion

# region sql query

def get_setting_record_log(d_ref, char=None):
    res = orm.SettingsRecordLog.slice(dep=d_ref, char = char)

    return list(res.dicts())

def get_time_acceptions(d_ref):
    dep = orm.Dep.get(orm.Dep.ref == d_ref)

    res = (orm.RightsAndSettings
                .select(orm.RightsAndSettings.object, orm.RightsAndSettings.settings, orm.RightsAndSettings.value_int)
                .where(orm.RightsAndSettings.object == dep.org.ref)
                .where(orm.RightAndSetting.name == 'Журнал электронной записи время приема')
                .join(orm.RightAndSetting, on=(orm.RightsAndSettings.settings == orm.RightAndSetting.ref)))

    res = res.dicts()

    listRAS = list(res)
    if len(listRAS) != 0:
         return int(listRAS[0]['value_int'])

    return TIME_ACCEPT

def get_time_begin(d_ref):   
    res = (orm.RightsAndSettings
                .select(orm.RightsAndSettings.object, orm.RightsAndSettings.settings, orm.RightsAndSettings.value_string)
                .where(orm.RightsAndSettings.object == d_ref)
                .where(orm.RightAndSetting.name == 'Журнал электронной записи время приема начало')
                .join(orm.RightAndSetting, on=(orm.RightsAndSettings.settings == orm.RightAndSetting.ref)))

    res = res.dicts()

    listRAS = list(res)
    if len(listRAS) != 0:
         return listRAS[0]['value_string']

    return TIME_BEGIN

def get_time_end(d_ref):
    res = (orm.RightsAndSettings
                .select(orm.RightsAndSettings.object, orm.RightsAndSettings.settings, orm.RightsAndSettings.value_string)
                .where(orm.RightsAndSettings.object == d_ref)
                .where(orm.RightAndSetting.name == 'Журнал электронной записи время приема окончание')
                .join(orm.RightAndSetting, on=(orm.RightsAndSettings.settings == orm.RightAndSetting.ref)))

    res = res.dicts()

    listRAS = list(res)
    if len(listRAS) != 0:
         return listRAS[0]['value_string']

    return TIME_END

def get_empl_dev(d_ref, date):  
    deps = []

    deps.append(d_ref)

    dep = orm.Dep.get(orm.Dep.ref == d_ref)

    if dep.org.code == 'CB000014' and dep.code == 'CB000104':
        dep = orm.Dep.get(orm.Dep.code == 'CB000407')
        deps.append(dep.ref)
    
    if dep.org.code == 'CB000019' or dep.org.code == 'CB000031':
        dep = orm.Dep.get(orm.Dep.code == 'CB000258')
        deps.append(dep.ref)
    
        dep = orm.Dep.get(orm.Dep.code == 'CB000128')
        deps.append(dep.ref)

    res = (orm.Workshop
                .select(orm.Workshop.ref)
                .where(orm.Workshop.dep << deps))

    res = res.dicts()

    list_res = list(res)
    
    workshops = []

    for x in list_res:
        workshops.append(x['ref'])
                
    date = datetime.now()
        
    date1 = date.replace(hour=0, minute=0, second=0, microsecond=0, day=1)

    res = (orm.EmployeeDevelopment
                .select(orm.EmployeeDevelopment.employee, peewee.fn.SUM(orm.EmployeeDevelopment.count))
                .where(orm.EmployeeDevelopment.workshop << workshops)
                .where(orm.EmployeeDevelopment.period == date1)
                .group_by(orm.EmployeeDevelopment.employee))

    res = res.dicts()

    return list(res)

def get_data_test_drive(d_ref, date):
    import decimal
    dep = orm.Dep.get(orm.Dep.ref == d_ref)

    #region empl

    res = (orm.WorksheetKIA
                .select(orm.Employee.ref.alias('m_ref'),
                    orm.Employee.name.alias('m_name'),
                    orm.Employee.phone.alias('m_phone'),
                    orm.Employee.ref_ones.alias('m_ref_ones'),
                    orm.Positions.name.alias('pos_name'),)       
                .join(orm.Employee, on=((orm.WorksheetKIA.employee == orm.Employee.ref)))
                .join(orm.JobMark, on=((orm.JobMark.ref == orm.WorksheetKIA.mark)))
                .where(orm.WorksheetKIA.dep == d_ref)
                .where(orm.WorksheetKIA.date == date)
                .where(orm.JobMark.name << orm.JobMark.getJobMarkWorkTime())
                .switch(orm.Employee)
                .join(orm.Positions, on=((orm.Employee.position == orm.Positions.ref))))
                
                #.where(orm.Positions.name << POSITIONS_LIST)            
                #.where(orm.Staff_Work_Schedule.dep == base64.b16decode(d_ref.encode()))

    res_empl = list(res.dicts())

    res = (orm.CRM_TestDrive
                .select(orm.CRM_TestDrive.mark.alias('r_mark'),
                    orm.CRM_TestDrive.posted.alias('r_post'),
                    orm.CRM_TestDrive.ref.alias('r_ref'),
                    orm.CRM_TestDrive.ref_ones.alias('r_ref_ones'),
                    orm.CRM_TestDrive.client.alias('c_ref'),
                    orm.CRM_TestDrive.notCome,
                    orm.CRM_TestDrive.reason,
                    orm.CRM_TestDrive.date.alias('r_begin'),
                    orm.CRM_TestDrive.periodEnd.alias('r_end'),

                    orm.Employee.ref.alias('m_ref'),
                    orm.Employee.name.alias('m_name'),
                    orm.Employee.phone.alias('m_phone'),
                    orm.Employee.ref_ones.alias('m_ref_ones'),
                    
                    orm.Positions.name.alias('pos_name'),

                    orm.ClientsCRM.name.alias('c_name'),
                    orm.ClientsCRM.ref.alias('client_ref'),

                    orm.Cars.name.alias('car_name'),
                    orm.Cars.ref.alias('car_ref'),

					orm.User.name.alias('user_name'),
                    orm.User.ref.alias('user_ref'),)           
                .join(orm.Employee, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Employee.ref == orm.CRM_TestDrive.employee)))
                .join(orm.ClientsCRM, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.ClientsCRM.ref == orm.CRM_TestDrive.client)))
                .join(orm.Cars, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Cars.ref == orm.CRM_TestDrive.car)))
                .join(orm.User, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.User.ref == orm.CRM_TestDrive.author)))
                .switch(orm.Employee)
                .join(orm.Positions, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Employee.position == orm.Positions.ref)))
                .where((orm.CRM_TestDrive.dep == d_ref) & (orm.CRM_TestDrive.date >= date) & (orm.CRM_TestDrive.date <= date + timedelta(days=1)) & (orm.CRM_TestDrive.mark == False)))   

    data = {}
    
    data['date_upd'] = datetime.now()

    data['empl'] = {}

    list_res = list(res.dicts())

    #for x in list_res:
    #    if x['pos_name'] == POS_NAME_SM:
    #        x['order1'] = 1000
    
    res_empl = sorted(res_empl, key=lambda e: e['m_name']) 
    res_empl = sorted(res_empl, key=lambda e: e['pos_name'])   
    #list_res = sorted(list_res, key=lambda e: e['order1'])

    list_records = []

    for x in res_empl:
        empls = data['empl']
        empl = empls.get(x['m_ref'])
        if empl is None:
            empl = {'m_ref' : x['m_ref'], 'm_name' : x['m_name'], 'm_phone' : x['m_phone'], 'm_ref_ones' : x['m_ref_ones'], 'periods':[], 'pos_name' : x['pos_name']}

            empls[x['m_ref']] = empl
    
    for x in list_res:
        empls = data['empl']
        empl = empls.get(x['m_ref'])
        if empl is None:
            empl = {'m_ref' : x['m_ref'], 'm_name' : x['m_name'], 'm_phone' : x['m_phone'], 'm_ref_ones' : x['m_ref_ones'], 'periods':[], 'pos_name' : x['pos_name']}

            empls[x['m_ref']] = empl

        empl['periods'].append(x)
        for i in  empl['periods']:
            if not i['r_ref'] is None:
                list_records.append(i['r_ref'])

            if i.get('r_begin', 0).year > 4000:                
                i['r_begin'] = i['r_begin'].replace(year = i['r_begin'].year - 2000)
                i['r_end'] = i['r_end'].replace(year = i['r_end'].year - 2000)


    ##endregion
    
    ##region posts

    data['eqip'] = {}

    #list_res = list(res.dicts())
   
    list_res = sorted(list_res, key=lambda e: e['car_name']) 

    for x in list_res:
        eqips = data['eqip']
        equip = eqips.get(x['car_ref'])
        if equip is None:
            equip = {'eq_ref' : x['car_ref'], 'eq_name' : x['car_name'], 'periods':[]}

            eqips[x['car_ref']] = equip

        equip['periods'].append(x)
        for i in  equip['periods']:
            if i.get('r_begin', 0).year > 4000:                
                i['r_begin'] = i['r_begin'].replace(year = i['r_begin'].year - 2000)
                i['r_end'] = i['r_end'].replace(year = i['r_end'].year - 2000)

    ##endregion

    return data

def get_data(d_ref, date, undistributed_works):
    import decimal
    dep = orm.Dep.get(orm.Dep.ref == d_ref)

    #region empl

    res = (orm.RecordToLogRecord
                .select(orm.Employee.ref.alias('m_ref'),
                    orm.Employee.name.alias('m_name'),
                    orm.Employee.phone.alias('m_phone'),
                    orm.Employee.ref_ones.alias('m_ref_ones'),

                    orm.RecordToLogRecord.mark.alias('r_mark'),
                    orm.RecordToLogRecord.posted.alias('r_post'),
                    orm.RecordToLogRecord.ref.alias('r_ref'),
                    orm.RecordToLogRecord.ref_ones.alias('r_ref_ones'),

                    orm.RecordToLogRecord.customer.alias('c_ref'),
                    orm.ClientsCRM.name.alias('c_name'),
                    orm.RecordToLogRecord.phone.alias('c_phone'),
                    orm.RecordToLogRecord.orderOutfit.alias('z_ref'),
                    orm.RecordToLogRecord.orderRepair.alias('q_ref'),

                    orm.RecordToLogRecord.notCome,

                    orm.RecordToLogRecord.reason,
                    orm.RecordToLogRecord.phone,              
                    
                    orm.RecordToLogRecord.carStr, 
                    orm.RecordToLogRecord.carNumber, 
                    orm.Contragent.name.alias('k_name'),
                    
                    orm.LogRecordKindWork.ref_ones.alias('kind_work_ref'),
                    
                    orm.Cars.name.alias('car_name'),
                    
                    orm.KindRepair.name.alias('kind_repair_name'),
					
					orm.User.name.alias('user_name'),

                    case(None, ((orm.OrderOutfit.posted == True, 'closed'),
                        (orm.RecordToLogRecord.orderOutfit != '', 'order'),
                        (orm.RecordToLogRecord.orderRepair != '', 'query'),), 'record').alias('type'),

                    case(None, ((orm.KindRepairCategory.name == KIND_REPAIR_NAME_GARANT, True),), False).alias('is_guarantee'),

                    local = False 

                    
                )
                .join(orm.RecordToLogRecord_Periods, on=((orm.RecordToLogRecord_Periods.ref == orm.RecordToLogRecord.ref)))
                .join(orm.LogRecordKindWork, on=((orm.LogRecordKindWork.ref == orm.RecordToLogRecord_Periods.kindWork)))
                .join(orm.ClientsCRM, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.ClientsCRM.ref == orm.RecordToLogRecord.customer)))
                .join(orm.OrderOutfit, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.OrderOutfit.ref == orm.RecordToLogRecord.orderOutfit)))
                .join(orm.KindRepair, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.KindRepair.ref == orm.RecordToLogRecord.kindRepair)))
                .join(orm.KindRepairCategory, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.KindRepairCategory.ref == orm.KindRepair.category)))    
                .join(orm.Contragent, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Contragent.ref == orm.RecordToLogRecord.contragent)))
                .join(orm.Cars, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Cars.ref == orm.RecordToLogRecord.car)))
                .join(orm.User, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.User.ref == orm.RecordToLogRecord.author))))
                
    res = (res
                .select(case(None, ((orm.RecordToLogRecord.ref >> None, orm.WorksheetKIA.date),), orm.RecordToLogRecord_Periods.periodStart).alias('r_begin'),
                    case(None, ((orm.RecordToLogRecord.ref >> None, orm.WorksheetKIA.date),), orm.RecordToLogRecord_Periods.periodEnd).alias('r_end'),    
                    
                    orm.Positions.name.alias('pos_name'),
                    
                    orm.RecordToLogRecord_Periods.num_str,

                    case(None, ((orm.Positions.name == POS_NAME_MP, 999),), 0).alias('order1'),  
                    )
                .join(orm.WorksheetKIA, join_type=peewee.JOIN.FULL, on=((orm.WorksheetKIA.employee == orm.RecordToLogRecord_Periods.employee) & (orm.RecordToLogRecord_Periods.periodStart >= date) & (orm.RecordToLogRecord_Periods.periodEnd < date + timedelta(days=1)) & (orm.RecordToLogRecord.mark == False) & (orm.RecordToLogRecord.posted == True) & (orm.RecordToLogRecord.notCome == False) & (orm.RecordToLogRecord.dep == dep)
                    ))
                .join(orm.JobMark, on=((orm.JobMark.ref == orm.WorksheetKIA.mark)))
                .join(orm.Employee, on=((orm.Employee.ref == orm.WorksheetKIA.employee)))
                .join(orm.Positions, on=((orm.Employee.position == orm.Positions.ref)))
                .slice(orm.Staff_Work_Schedule.employee,
                    on = ((orm.WorksheetKIA.employee == orm.Staff_Work_Schedule.employee)))
                .join(orm.KindsShedule, on=((orm.KindsShedule.ref == orm.Staff_Work_Schedule.kindShedule)))
                .where(orm.WorksheetKIA.dep == dep)
                .where(orm.WorksheetKIA.date == date)
                .where(orm.JobMark.name << orm.JobMark.getJobMarkWorkTime())
                .where(orm.Positions.name << POSITIONS_LIST)            
                .where(orm.Staff_Work_Schedule.dep == base64.b16decode(d_ref.encode()))
                )

    data = {}
    count = 0

    data['date_upd'] = datetime.now()

    data['empl'] = {}

    list_res = list(res.dicts())

    for x in list_res:
        if x['pos_name'] == POS_NAME_SM:
            x['order1'] = 1000
    
    list_res = sorted(list_res, key=lambda e: e['m_name']) 
    list_res = sorted(list_res, key=lambda e: e['pos_name'])   
    list_res = sorted(list_res, key=lambda e: e['order1'])

    list_records = []

    for x in list_res:
        empls = data['empl']
        empl = empls.get(x['m_ref'])
        if empl is None:
            empl = {'m_ref' : x['m_ref'], 'm_name' : x['m_name'], 'm_phone' : x['m_phone'], 'm_ref_ones' : x['m_ref_ones'], 'periods':[], 'pos_name' : x['pos_name']}

            empls[x['m_ref']] = empl

        empl['periods'].append(x)
        for i in  empl['periods']:
            if not i['r_ref'] is None:
                list_records.append(i['r_ref'])
            
            if i.get('r_begin', 0).year > 4000:                
                i['r_begin'] = i['r_begin'].replace(year = i['r_begin'].year - 2000)
                i['r_end'] = i['r_end'].replace(year = i['r_end'].year - 2000)


    #endregion
    
    #region posts

    res = (orm.RecordToLogRecord
                .select(orm.WorkshopEquipment.ref.alias('eq_ref'),
                    orm.WorkshopEquipment.name.alias('eq_name'),
                    
                    orm.WorkshopEquipment.ref_ones.alias('eq_ref_ones'),

                    orm.RecordToLogRecord.mark.alias('r_mark'),
                    orm.RecordToLogRecord.posted.alias('r_post'),
                    orm.RecordToLogRecord.ref.alias('r_ref'),
                    orm.RecordToLogRecord.ref_ones.alias('r_ref_ones'),

                    orm.RecordToLogRecord.customer.alias('c_ref'),
                    orm.ClientsCRM.name.alias('c_name'),
                    orm.RecordToLogRecord.phone.alias('c_phone'),
                    orm.RecordToLogRecord.orderOutfit.alias('z_ref'),
                    orm.RecordToLogRecord.orderRepair.alias('q_ref'),

                    orm.RecordToLogRecord.notCome,

                    orm.RecordToLogRecord.reason,
                    orm.RecordToLogRecord.phone,              
                    
                    orm.RecordToLogRecord.carStr, 
                    orm.RecordToLogRecord.carNumber, 
                    orm.Contragent.name.alias('k_name'),
                    
                    orm.LogRecordKindWork.ref_ones.alias('kind_work_ref'),
                    
                    orm.Cars.name.alias('car_name'),
                    
                    orm.KindRepair.name.alias('kind_repair_name'),
					
					orm.User.name.alias('user_name'),

                    case(None, ((orm.OrderOutfit.posted == True, 'closed'),
                        (orm.RecordToLogRecord.orderOutfit != '', 'order'),
                        (orm.RecordToLogRecord.orderRepair != '', 'query'),), 'record').alias('type'),

                    case(None, ((orm.KindRepairCategory.name == KIND_REPAIR_NAME_GARANT, True),), False).alias('is_guarantee'),

                    local = False    
                )
                .join(orm.RecordToLogRecord_Periods, on=((orm.RecordToLogRecord_Periods.ref == orm.RecordToLogRecord.ref)))
                .join(orm.LogRecordKindWork, on=((orm.LogRecordKindWork.ref == orm.RecordToLogRecord_Periods.kindWork)))
                .join(orm.ClientsCRM, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.ClientsCRM.ref == orm.RecordToLogRecord.customer)))
                .join(orm.OrderOutfit, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.OrderOutfit.ref == orm.RecordToLogRecord.orderOutfit)))
                .join(orm.KindRepair, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.KindRepair.ref == orm.RecordToLogRecord.kindRepair)))
                .join(orm.KindRepairCategory, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.KindRepairCategory.ref == orm.KindRepair.category)))    
                .join(orm.Contragent, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Contragent.ref == orm.RecordToLogRecord.contragent)))
                .join(orm.Cars, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.Cars.ref == orm.RecordToLogRecord.car)))
                .join(orm.User, join_type=peewee.JOIN.LEFT_OUTER, on=((orm.User.ref == orm.RecordToLogRecord.author))))
                
    res = (res
                .select((orm.RecordToLogRecord_Periods.periodStart).alias('r_begin'),
                    (orm.RecordToLogRecord_Periods.periodEnd).alias('r_end'),    
                    
                    orm.RecordToLogRecord_Periods.num_str,
                   
                    )
                .join(orm.WorkshopEquipment, join_type=peewee.JOIN.INNER, on=(orm.WorkshopEquipment.ref == orm.RecordToLogRecord_Periods.employee))
                .where((orm.RecordToLogRecord_Periods.periodStart >= date) & (orm.RecordToLogRecord_Periods.periodEnd < date + timedelta(days=1)) & (orm.RecordToLogRecord.mark == False) & (orm.RecordToLogRecord.posted == True) & (orm.RecordToLogRecord.notCome == False) & (orm.RecordToLogRecord.dep == dep)))

    data['eqip'] = {}

    list_res = list(res.dicts())
   
    list_res = sorted(list_res, key=lambda e: e['eq_name']) 

    for x in list_res:
        eqips = data['eqip']
        equip = eqips.get(x['eq_ref'])
        if equip is None:
            equip = {'eq_ref' : x['eq_ref'], 'eq_name' : x['eq_name'], 'eq_ref_ones' : x['eq_ref_ones'], 'periods':[], 'eq_name' : x['eq_name']}

            eqips[x['eq_ref']] = equip

        equip['periods'].append(x)
        for i in  equip['periods']:
            if i.get('r_begin', 0).year > 4000:                
                i['r_begin'] = i['r_begin'].replace(year = i['r_begin'].year - 2000)
                i['r_end'] = i['r_end'].replace(year = i['r_end'].year - 2000)

    #endregion

    #region undistributed works

    list_records = list(set(list_records))

    res = (orm.RecordToLogRecord_Periods
                .select(orm.RecordToLogRecord_Periods.key_periods_repair, 
                        orm.RecordToLogRecord_Periods.periodStart, 
                        orm.RecordToLogRecord_Periods.periodEnd, 
                        orm.RecordToLogRecord_Periods.num_str)

                .where((orm.RecordToLogRecord_Periods.ref << list_records) & 
                (orm.RecordToLogRecord_Periods.key_periods_repair != '')))

    res = res.dicts()

    list_keys_periods_repair = list(res)

    res = (orm.ServiceRecord
                .select(orm.ServiceRecord.ref,
                        orm.ServiceRecord.recordLR,

                        orm.ServiceRecord_Services.service,
                        orm.ServiceRecord_Services.amount,
                        orm.ServiceRecord_Services.work_hour,
                        orm.ServiceRecord_Services.num_str,
                        orm.ServiceRecord_Services.key_periods_repair,

                        peewee.fn.CONCAT(orm.Services.name, '').alias('service_name')

                        )

                .join(orm.ServiceRecord_Services, on=(orm.ServiceRecord.ref == orm.ServiceRecord_Services.link))
                .join(orm.Services, on=(orm.ServiceRecord_Services.service == orm.Services.ref))
                #.where((orm.ServiceRecord.recordLR << list_records) & 
                #       (orm.ServiceRecord.started == True) &
                #       (~(orm.ServiceRecord_Services.key_periods_repair << [item['key_periods_repair'] for item in list_keys_periods_repair]))))
                 .where((orm.ServiceRecord.recordLR << list_records) & 
                       (orm.ServiceRecord.started == True)))
            
    res = res.dicts()

    if undistributed_works.get(d_ref) is None:
        undistributed_works[d_ref] = {}

    works = undistributed_works.get(d_ref)
    
    for x in list(res):
        if works.get(x['recordLR']) is None:
            works[x['recordLR']] = []
        
        ref = works.get(x['recordLR'])

        hours_total = 0
        hours_plan = x['work_hour'] * x['amount']

        if len(x['key_periods_repair']) != 0: 
            for y in list_keys_periods_repair:
                if x['key_periods_repair'] == y['key_periods_repair']:
                    hours_total = hours_total + (decimal.Decimal)((y['periodEnd'] - y['periodStart']).seconds /3600)

        #round(hours_total - hours_plan, 2) = 

        if round(hours_plan - hours_total, 2) == (decimal.Decimal)(0):
            continue

        x['hours_total'] = hours_plan - hours_total

        is_exist = False
        for w in works[x['recordLR']]:
            if w['hours_total'] == x['hours_total'] and w['key_periods_repair'] == x['key_periods_repair']:
                is_exist = True

        if not is_exist:
            ref.append(x)

    #endregion

    return data

def get_dep_work_time(d_ref, date):       
    d = {}
   
    query_text = f"""
    SELECT [empl]
      ,[period]
      ,[period_offset]
      ,[period_value]
      ,[period_date_time]
    FROM [ex_working_hours].[dbo].[v_work_hours_date]
    WHERE dep = '{d_ref}' AND period = CONVERT(DATETIME, '{date.strftime("%Y-%d-%m %H:%M")}', 103)
    ORDER BY period_date_time ASC"""

    #query_text = query_text.replace('%dep%', 'dep = \'' + d_ref + '\'')
    #query_text = query_text.replace('%period%', 'period = CONVERT(DATETIME,\'' + date.strftime("%Y-%d-%m %H:%M") + '\', 103)')
    
    cursor = get_mssql_conn()

    cursor.execute(query_text)  
    row = cursor.fetchone()  
    while row: 
        empl = row[0].upper() 

        if d.get(empl) is None:
            d[empl] = {'all_time':[], 'not_working_time':[], 'working_time':[], 'lunch_time':[]}

        d_empl = d.get(empl)

        d_empl['all_time'].append({'period_value':row[3], 'period_date_time':row[4]})

        if row[3] == 0:
            d_empl['not_working_time'].append({'period_value':row[3], 'period_date_time':row[4]})

        elif row[3] == 1:
            d_empl['working_time'].append({'period_value':row[3], 'period_date_time':row[4]})

        elif row[3] == 2:
            d_empl['lunch_time'].append({'period_value':row[3], 'period_date_time':row[4]})

        row = cursor.fetchone()  

    return d

def get_mssql_conn(sql_base=''):
    #sql_host = conn_string.sql_host
    #sql_user = conn_string.sql_user
    #sql_pass = conn_string.sql_pass
    #sql_base_ex_w_h = conn_string.sql_base_ex_w_h

    sql_host = SQL_HOST_EX_W_H_DEFAULT
    sql_user = SQL_USER_EX_W_H_DEFAULT
    sql_pass = SQL_PASS_EX_W_H_DEFAULT
    sql_base = SQL_BASE_EX_W_H_DEFAULT

    conn = pymssql.connect(server=sql_host, user=sql_user, password=sql_pass, database=sql_base)  
    cursor = conn.cursor()  

    return cursor

def get_data_brigades():
    res = (orm.DataBrigade
                .select(orm.DataBrigade.expert, orm.DataBrigade.master, orm.DataBrigade.brigade, orm.Brigades.name)
                .join(orm.Brigades, on=(orm.Brigades.ref == orm.DataBrigade.brigade)))


    res = list(res.dicts())

    res = sorted(res, key=lambda e: e['name']) 

    return res

# endregion

def json_serial(obj):
    from datetime import datetime, date
    import decimal
    if isinstance(obj, (datetime, date)):
       return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
       return float(obj)
    pass

