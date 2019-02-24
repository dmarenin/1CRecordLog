from datetime import datetime
from flask import render_template, request
from server import app, CACHE, CACHE_DEP, EMPL_DEV, WORK_TIME, UNDISTRIDUTED_WORKS
import server.updater as updater 
from server.consts import *
import json
from server.res_to_vis_js import res_to_vis_js, res_to_vis_js_test_drive
import orm.models as orm 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/timeline2')
def timeline1():
    return render_template('timeline2.html')

@app.route('/timeline_sale')
def timeline_test_drive():
    return render_template('timeline_sale.html')

# region api

# region service

@app.route('/get')
def get():
    d_ref = request.args.get('d_ref', '').upper() 
    
    r_ref = request.args.get('r_ref', '').upper()     
    if len(r_ref) == 0:
        r_ref = None

    date = request.args.get('date', '').upper() 
    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) 
    
    is_garant = request.args.get('is_garant', '').upper()     
    is_garant = is_garant == 'ДА'
    
    res = updater.get(d_ref, date, r_ref, is_garant)

    empl_dev = EMPL_DEV.get(d_ref)

    dep_work_time = []
    if not WORK_TIME.get(d_ref) is None:
        dep_work_time = WORK_TIME[d_ref][date]
    
    work_time_posts = []                        
    list_time_reserved = []
    if not CACHE_DEP.get(d_ref) is None:
        list_time_reserved = CACHE_DEP.get(d_ref)['list_time_reserved']
        work_time_posts = CACHE_DEP.get(d_ref)['work_time_posts']
    
    undistributed_works = []
    if not UNDISTRIDUTED_WORKS.get(d_ref) is None:
        undistributed_works = UNDISTRIDUTED_WORKS.get(d_ref) 
    
    res = res_to_vis_js(res, date, dep_work_time, list_time_reserved, r_ref, is_garant, empl_dev, work_time_posts, undistributed_works)

    res = json.dumps(res, default=json_serial)
 
    return res, 200, HEADERS

@app.route('/upd')
def upd():
    d_ref = request.args.get('d_ref', '').upper() 
    
    date = request.args.get('date', '').upper() 
    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) 
    
    updater.add_to_upd_event_list(d_ref, date, 0)
    
    return S_OK, 200, HEADERS
   
@app.route('/upd_from_order')
def upd_from_order():
    r_ref = request.args.get('r_ref', '').upper() 
    d_ref = request.args.get('d_ref', '').upper() 
    
    if len(r_ref) == 0:
        return S_OK, 200, HEADERS

    EMPL_DEV[d_ref] = None

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
            
        updater.add_to_upd_event_list(d_ref, date, 0)

    return S_OK, 200, HEADERS

@app.route('/upd_from_invoice')
def upd_from_invoice():
    r_ref = request.args.get('r_ref', '').upper() 
    d_ref = request.args.get('d_ref', '').upper() 
    
    if len(r_ref) == 0:
        return S_OK, 200, HEADERS

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
            
        updater.add_to_upd_event_list(d_ref, date, 0)

    return S_OK, 200, HEADERS

@app.route('/upd_from_worksheet')
def upd_from_worksheet():
    d_ref = request.args.get('d_ref', '').upper() 
    
    if len(d_ref) == 0:
        return S_OK, 200, HEADERS

    if not WORK_TIME.get(d_ref) is None:
        work_time = WORK_TIME.get(d_ref)

        del WORK_TIME[d_ref]

    if not CACHE.get(d_ref) is None:
        CACHE[d_ref] = None 
        CACHE_DEP[d_ref] = None
       
    return S_OK, 200, HEADERS

# endregion

# region sale

@app.route('/get_sale')
def get_sale():
    d_ref = request.args.get('d_ref', '').upper() 
    
    r_ref = request.args.get('r_ref', '').upper()     
    if len(r_ref) == 0:
        r_ref = None

    date = request.args.get('date', '').upper() 
    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    res = updater.get_test_drive(d_ref, date)

    dep_work_time = WORK_TIME[d_ref][date]

    res = res_to_vis_js_test_drive(res, date, r_ref, dep_work_time)

    res = json.dumps(res, default=json_serial)
 
    return res, 200, HEADERS

@app.route('/upd_from_test_drive')
def upd_from_test_drive():
    d_ref = request.args.get('d_ref', '').upper() 
    
    date = request.args.get('date', '').upper() 
    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    date = date.replace(hour=0, minute=0, second=0, microsecond=0) 
    
    updater.add_to_upd_event_list(d_ref, date, 1)
    
    return S_OK, 200, HEADERS
    
# endregion

# endregion

def json_serial(obj):
    from datetime import datetime, date
    import decimal
    if isinstance(obj, (datetime, date)):
       return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
       return float(obj)
    pass

