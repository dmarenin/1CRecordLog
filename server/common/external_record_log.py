# coding:utf-8

from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
from urllib.parse import urlparse, parse_qs
import socket
import threading
from datetime import datetime
from datetime import timedelta

from common.consts import *

from common import common
from common.orm import models as orm
import peewee
from playhouse.shortcuts import case
import base64
import sys
import pymssql
import uuid
import time
import _thread



class ExternalRecordLog_Exception(Exception):
    pass

class ExternalRecordLog_Handler(BaseHTTPRequestHandler):
    callback = None

    def log_message(self, format, *args):
        return

    def smart_response(self, code, message, headers=[]):
        self.send_response(code)
        for h, v in headers:
            self.send_header(h, v)
        self.end_headers()
        if (code != 200):
            print(message)
            message = "<br><br><br><center><h2>" + message.encode('utf-8').decode() + "</h2>"

        return self.wfile.write(message.encode())

    def do_GET(self):
        path = urlparse(self.path).path
        qs = urlparse(self.path).query
        qs = parse_qs(qs)
        
        res = self.callback(path, qs, self)

class ExternalRecordLog():
    server = None
    parser = common.createParser()
    namespace = parser.parse_args(sys.argv[1:])
    server_host = namespace.ip
    server_port = int(namespace.port)
    handler = ExternalRecordLog_Handler
    
    cache = {}
    cache_dep = {}
    empl_dev = {}    
    work_time = {}
    undistributed_works = {}

    upd_event_lists = []

    req_count_all = 0
    req_count_hit = 0
    req_count_fault = 0
    req_count_upd = 0

    def __init__(self, caller=None):
        self.handler.callback = self.callback
        
        self.upd_event_lists.append([])
        self.upd_event_lists.append([])
        self.upd_event_lists.append([])
        self.upd_event_lists.append([])

        self.upd_event_lists.append([])
        self.upd_event_lists.append([])
        self.upd_event_lists.append([])
        self.upd_event_lists.append([])

        for i, val in enumerate(self.upd_event_lists):
            _thread.start_new_thread(self.upd_loop, (i,))

    def callback(self, path, qs, handler):
        while path and path[0] == '/':
            path = path[1:]

            if path =='favicon.ico':
                continue
            
            d_ref = None
            date = None
            r_ref = None
            is_garant = None

            fn = None

            if qs.get('d_ref'):              
                d_ref = qs.get('d_ref')[0].upper()

            if qs.get('date'):              
                date = qs.get('date')[0].upper()
                date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

                date = date.replace(hour=0, minute=0, second=0, microsecond=0)

            if qs.get('r_ref'):              
                r_ref = qs.get('r_ref')[0].upper()

            if qs.get('is_garant'):              
                is_garant = qs.get('is_garant')[0]

                is_garant = is_garant == 'Да'

            if qs.get('fn'):              
                fn = qs.get('fn')[0].upper()
             
            self.req_count_all += 1

            try:
                res = eval('self.%s(d_ref, date, r_ref, is_garant)' % path)
            except KeyError as e:
                return handler.smart_response(500, "Не задано значение параметра: %s" % e)
            except ValueError as e:
                return handler.smart_response(500, "Ошибка в значении параметра: %s" % e)
            except ExternalRecordLog_Exception as e:
                return handler.smart_response(500, "%s" % e)
            except Exception as e:
                return handler.smart_response(500, "Неожиданная ошибка: %s" % e)

            if not res:
                res = json.dumps([], default=common.json_serial)
                content_type = "application/json"

            else:             
                empl_dev = self.empl_dev.get(d_ref)

                if path == 'get':
                    dep_work_time = []
                    if not self.work_time.get(d_ref) is None:
                        dep_work_time = self.work_time[d_ref][date]
                        
                    list_time_reserved = []
                    if not self.cache_dep.get(d_ref) is None:
                        list_time_reserved = self.cache_dep.get(d_ref)['list_time_reserved']
                        
                    work_time_posts = []
                    if not self.cache_dep.get(d_ref) is None:
                        work_time_posts = self.cache_dep.get(d_ref)['work_time_posts']
                        
                    res = res_to_vis_js(res, date, dep_work_time, list_time_reserved, r_ref, is_garant, empl_dev, work_time_posts, self.undistributed_works.get(d_ref))

                res = json.dumps(res, default=common.json_serial)

            try:
                handler.smart_response(200, res, [
                    ("Access-Control-Allow-Origin", "*"),
                    ("Access-Control-Expose-Headers", "Access-Control-Allow-Origin"),
                    ("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept"),])
            except socket.error as e:
                pass

            return
        else:
            handler.smart_response(401, "Unauthorized call: %s from %s" % (path, handler.client_address))
    
    def get(self, d_ref, date=None, r_ref=None, is_garant=None):
        if self.cache_dep.get(d_ref) is None:
            time_begin = get_time_begin(d_ref)
            time_end = get_time_end(d_ref)

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


            self.cache_dep[d_ref] = {'time_end' : time_end, 'time_acceptions' : time_acceptions, 'time_begin' : time_begin, 'list_time_reserved' : list_time_reserved, 'work_time_posts':work_time_posts}

        time_acceptions = self.cache_dep.get(d_ref)['time_acceptions']        
        time_begin = self.cache_dep.get(d_ref)['time_begin']      
        time_end = self.cache_dep.get(d_ref)['time_end']
        list_time_reserved = self.cache_dep.get(d_ref)['list_time_reserved']
        work_time_posts = self.cache_dep.get(d_ref)['work_time_posts']

        if self.empl_dev.get(d_ref) is None:
            self.empl_dev[d_ref] = get_empl_dev(d_ref, date) 

        if self.work_time.get(d_ref) is None:
            self.work_time[d_ref] = {}

        if not date is None:
            dep_work_time = self.work_time[d_ref]
        
            if dep_work_time.get(date) is None:
                dep_work_time = get_dep_work_time(d_ref, date, self.namespace)

                self.work_time[d_ref].update({date : dep_work_time})

        if self.cache.get(d_ref) is None:
            self.cache[d_ref] = {}

        cache_dep = self.cache.get(d_ref)
        if cache_dep.get(date) is None:
            res = get_data(d_ref, date, self.undistributed_works)

            self.req_count_fault += 1
                             
            res['time_acceptions'] = time_acceptions
            res['time_begin'] = time_begin
            res['time_end'] = time_end

            if not self.cache.get(d_ref) is None:
                self.cache[d_ref][date] = res 
            
        else:
            res = cache_dep.get(date)   
                
            self.req_count_hit += 1

        return res

    def do_upd_loop(self, ind_upd_list):
        t_loop = 0.050
        for x in self.upd_event_lists[ind_upd_list]:   
            d_ref = x['d_ref']
            date = x['date'] 

            self.upd_event_lists[ind_upd_list].remove(x)

            if self.cache.get(d_ref) is None:
                continue
           
            if not self.cache.get(d_ref) is None:
                self.cache[d_ref][date] = None 
            
            if not self.undistributed_works.get(d_ref) is None:
                self.undistributed_works[d_ref] = None

            try:
                self.get(d_ref, date)
            except:
                continue

            if d_ref == DEP_FORD:
                tsdate = int(date.timestamp())
                try:
                    jsonurl = urllib.request.urlopen('http://dev.agrad.ru/api__unsafe2_send_upd_records?d_ref=' + str(d_ref) + '&date=' + str(tsdate))
                except:
                    pass

        time.sleep(t_loop)

    def upd_loop(self, ind_upd_list):
        while True:
            self.do_upd_loop(ind_upd_list)

    def clear(self, d_ref, date, r_ref=None, is_garant=None):
        self.cache = {}
        self.cache = {}
        self.cache_dep = {}
        self.empl_dev = {}
        self.work_time = {}
        self.self.upd_event_list = []

        return S_OK

    def view(self, d_ref, date, r_ref=None, is_garant=None):
        res = {}

        for x in self.cache:
            res[x] = []

            for y in self.cache.get(x):
                res[x].append(y)

        return json.dumps(res, default=common.json_serial)
     
    def req_view(self, d_ref, date, r_ref=None, is_garant=None):
        res = {'req_count_all':self.req_count_all, 'req_count_hit':self.req_count_hit, 'req_count_fault':self.req_count_fault, 'req_count_upd':self.req_count_upd, 'upd_event_lists':self.upd_event_lists}
  
        return json.dumps(res, default=common.json_serial)

    def add_to_upd_event_list(self, d_ref, date):        
        lens = []

        for i, val in enumerate(self.upd_event_lists):
            lens.append((len(self.upd_event_lists[i]), i))

        min_list = min(lens)

        self.upd_event_lists[min_list[1]].append({ 'd_ref':d_ref, 'date':date })

    def upd(self, d_ref, date, r_ref=None, is_garant=None):  
        self.req_count_upd += 1

        self.add_to_upd_event_list(d_ref, date)

        return S_OK
    
    def upd_from_order(self, d_ref=None, date=None, r_ref=None, is_garant=None):
        self.req_count_upd += 1
        if r_ref is None:
            return S_OK

        self.empl_dev[d_ref] = None

        res = (orm.RecordToLogRecord
                .select(orm.RecordToLogRecord.ref.alias('r_ref'),
                    orm.RecordToLogRecord.dep.alias('d_ref'),
                    orm.RecordToLogRecord.ref_ones.alias('r_ref_ones'),       
                    orm.RecordToLogRecord.orderOutfit.alias('z_ref'),
                    orm.RecordToLogRecord.orderRepair.alias('q_ref'),
                    orm.RecordToLogRecord_Periods.periodStart.alias('r_begin'),
                    orm.RecordToLogRecord_Periods.periodEnd.alias('r_end'),)
                .join(orm.RecordToLogRecord_Periods, on=((orm.RecordToLogRecord_Periods.ref == orm.RecordToLogRecord.ref)))
                
                .where(orm.RecordToLogRecord.orderOutfit == r_ref))

        list_res = list(res.dicts())

        for x in list_res:
            d_ref = x['d_ref']
            date = x['r_begin'] 

            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.add_to_upd_event_list(d_ref, date)

        return S_OK
    
    def upd_from_invoice(self, d_ref=None, date=None, r_ref=None, is_garant=None):
        self.req_count_upd += 1
        if r_ref is None:
            return S_OK

        res = (orm.RecordToLogRecord
                .select(orm.RecordToLogRecord.ref.alias('r_ref'),
                    orm.RecordToLogRecord.dep.alias('d_ref'),
                    orm.RecordToLogRecord.ref_ones.alias('r_ref_ones'),                   
                    orm.RecordToLogRecord.orderOutfit.alias('z_ref'),
                    orm.RecordToLogRecord.orderRepair.alias('q_ref'),
                    orm.RecordToLogRecord_Periods.periodStart.alias('r_begin'),
                    orm.RecordToLogRecord_Periods.periodEnd.alias('r_end'),)
                .join(orm.RecordToLogRecord_Periods, on=((orm.RecordToLogRecord_Periods.ref == orm.RecordToLogRecord.ref)))
                
                .where(orm.RecordToLogRecord.orderRepair == r_ref))

        list_res = list(res.dicts())

        for x in list_res:
            d_ref = x['d_ref']
            date = x['r_begin'] 
                          
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.add_to_upd_event_list(d_ref, date)

        return S_OK

    def upd_from_worksheet(self, d_ref, date=None, r_ref=None, is_garant=None):
        self.req_count_upd += 1
        if not self.work_time.get(d_ref) is None:
            work_time = self.work_time.get(d_ref)

            del self.work_time[d_ref]

        if not self.cache.get(d_ref) is None:
            self.cache[d_ref] = None 
            self.cache_dep[d_ref] = None
       
        return S_OK



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

def get_data(d_ref, date, undistributed_works):
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
                .where(orm.Staff_Work_Schedule.dep == base64.b16decode(d_ref.encode())))

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
                .where((orm.ServiceRecord.recordLR << list_records) & 
                       (orm.ServiceRecord.started == True) &
                       (~(orm.ServiceRecord_Services.key_periods_repair << [item['key_periods_repair'] for item in list_keys_periods_repair]))))
            
    res = res.dicts()

    if undistributed_works.get(d_ref) is None:
        undistributed_works[d_ref] = {}

    works = undistributed_works.get(d_ref)

    for x in list(res):
        if works.get(x['recordLR']) is None:
            works[x['recordLR']] = []
        
        ref = works.get(x['recordLR'])

        ref.append(x)

    #endregion

    return data

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

    style = "color: white; background-color: #999999;"
    eq = []
    className = 'openwheel'
    order = 100

    for e in eqips:
        val += 1
        order +=1

        eqip = eqips.get(e)

        hours_in_day = ((date + timedelta(hours=int(data['time_end'][0:2]))) - (date + timedelta(hours=int(data['time_begin'][0:2])))).seconds / 3600

        data['time_end']

        total_hours = 0

        for y in eqip['periods']:
            total_hours += (y['r_end'] - y['r_begin']).seconds/3600

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

        date_start = date + timedelta(hours=int(data['time_begin'][0:2]))
        date_stop = date + timedelta(days=1)
            
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
                        timeline['works'].append({'name': f""" {y['service_name']} ({round(y['work_hour']*y['amount'] ,2)} ч)""", 'service':y['service'], 'ref':y['ref'], 'num_str':y['num_str'], 'amount':y['work_hour']*y['amount']})

    #endregion
    
    return data

def get_dep_work_time(d_ref, date, conn_string):       
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
    
    cursor = get_mssql_conn(conn_string)

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

def get_mssql_conn(conn_string, sql_base=''):
    sql_host = conn_string.sql_host
    sql_user = conn_string.sql_user
    sql_pass = conn_string.sql_pass
    sql_base_ex_w_h = conn_string.sql_base_ex_w_h

    sql_host = '192.168.5.60'
    sql_user = 'sa'
    sql_pass = '20SenseY13*'

    conn = pymssql.connect(server=sql_host, user=sql_user, password=sql_pass, database=sql_base_ex_w_h)  
    cursor = conn.cursor()  

    return cursor

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

