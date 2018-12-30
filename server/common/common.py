# coding:utf-8
from datetime import datetime, date
import base64
import re
import threading
import argparse

import decimal

from common.consts import *

datetime_format = "%Y-%m-%dT%H:%M:%S"
datetime_format_regex = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-ip', '--ip', default=IP_DEFAULT)
    parser.add_argument ('-port', '--port', default=PORT_DEFAULT)
    parser.add_argument ('-sql_host', '--sql_host', default=SQL_HOST_DEFAULT)
    parser.add_argument ('-sql_base', '--sql_base', default=SQL_BASE_DEFAULT)
    parser.add_argument ('-sql_user', '--sql_user', default=SQL_USER_DEFAULT)
    parser.add_argument ('-sql_pass', '--sql_pass', default=SQL_PASS_DEFAULT)
    parser.add_argument ('-sql_base_ex_w_h', '--sql_base_ex_w_h', default=SQL_BASE_EX_W_H_DEFAULT)
 
    return parser

def makepack(data):
  pack = {}
  for line in data.splitlines():
    if line == '': continue
    s = line.split(': ', 1)
    k = str(s[0])
    if len(s) == 1:
        pack[k.lower()] = None
    else:
        pack[k.lower()] = s[1]
  return pack

def mk_rec_path(caller, called, direction = 'transfer'):
  return conf.rec.format(datetime.now()) % (direction, caller, called)

def encrypt(key, clear):
  enc = []
  for i in range(len(clear)):
    key_c = key[i % len(key)]
    enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
    enc.append(enc_c)
  enc = base64.urlsafe_b64encode("".join(enc).encode())
  return enc.decode()

def decrypt(key, enc):
  dec = []
  enc = base64.urlsafe_b64decode(enc).decode()
  for i in range(len(enc)):
      key_c = key[i % len(key)]
      dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
      dec.append(dec_c)
  clear = "".join(dec)
  return clear

def lock(sem, mark = 'UNKNOWN', clear = True, timeout = None):
  #clear = clear and not sem.ready()

  if clear:
    sem.clear()



  sem.wait(timeout)



def unlock(sem, mark = 'UNKNOWN', check = True):
  check = check and sem.ready()



  if check:
    return

  sem.set()

def json_serial(obj):
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()

  if isinstance(obj, decimal.Decimal):
    return float(obj)

  raise TypeError("Type is not serializable %s" % type(obj))

def date_hook(json_dict):
  for (key, value) in json_dict.items():
    if type(value) is str and re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d*$', value):
      json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    elif type(value) is str and re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', value):
      json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    else:
      pass

  return json_dict

def datetime_parser(dct):
  for k, v in dct.items():
    if isinstance(v, str) and datetime_format_regex.match(v):
      dct[k] = datetime.strptime(v, datetime_format)
  return dct

def print_query(query, params = False):
    import sqlparse
    print(sqlparse.format(query[0], reindent_aligned = True, strip_whitespace = True))
    # print(query[0]
    #       .replace("SELECT", "\n\nSELECT")
    #       .replace("FROM", "\nFROM")
    #       .replace("WHERE", "\nWHERE")
    #       .replace("INNER", "\n  INNER")
    #       .replace("LEFT", "\n  LEFT")
    #       .replace("ON", "\n  ON")
    #       # .replace(" AS", "\n  AS")
    # )
    if params:
        print("Params:", query[1])
        # print("Params:")
        # for n, p in enumerate(query[1], 1):
        #     print(n, p)

'''
 Decorators
'''
def debug_args(slave):
    def wrapper(*args, **kwargs):

        for arg in args:
            arg and debug.log(" ", arg, level = debug.green)
       
        res = slave(*args, **kwargs)
        return res
    return wrapper

def debug_result(slave):
    def wrapper(*args, **kwargs):
        res = slave(*args, **kwargs)

        return res
    return wrapper


