import peewee
import peewee_mssql
import time
import threading
import sys


from .fields import * 
from datetime import datetime

from server.conf import SQL_HOST, SQL_BASE, SQL_USER, SQL_PASS



class LegacyDatabase(peewee_mssql.MssqlDatabase):
    def execute_sql(self, sql, params=None, require_commit=True):
        try:
            return super().execute_sql(sql, params, require_commit)
        except peewee.ProgrammingError as e:
            common.print_query((sql,params), True)
            if len(e.args) > 1:
                pass
            else:
                raise e

class LocalDatabase(peewee.SqliteDatabase):
    pass

import os
try:
    os.remove('/tmp/test.db')
except Exception:
    pass

class ModelAlias(peewee.ModelAlias):

    def select(self, *selection, **kwargs):
        local = kwargs.pop('local', None)

        if not selection:
            selection = self.get_proxy_fields()
        query = SelectQuery(self, *selection, **kwargs)
        if self._meta.order_by:
            query = query.order_by(*self._meta.order_by)
        return query


class SelectQuery(peewee.SelectQuery):
    def __init__(self, model_class, *selection, **kwargs):
        super().__init__(model_class, *selection)
        self.local = kwargs.get('local', True)
        self.slice_aliases = {}

    def clone(self):
        inst = super().clone()
        inst.local = self.local
        inst.slice_aliases = self.slice_aliases
        return inst

    def select(self, *selection, **kwargs):
        if self._select:
            self._select += self._model_shorthand(selection)
            return self

        query = SelectQuery(self, *selection, **kwargs)
        if self._meta.order_by:
            query = query.order_by(*self._meta.order_by)
        return query

    def swap_slices(self, fieldset):
        if fieldset is None: return

        def swap_field(field):
            if issubclass(type(field), peewee.Field):
                for alias, val in self.slice_aliases.items():
                    cls, c = val
                    if cls == field.model_class:
                        new_field = getattr(c, field.db_column)
                        new_field._alias = field._alias
                        return new_field
            return field

        # SELECT
        if isinstance(fieldset, list):
            for k, field in enumerate(fieldset):
                fieldset[k] = swap_field(field)
            return fieldset

        # WHERE
        elif isinstance(fieldset, peewee.Expression):
            def branch(field):
                if isinstance(field, peewee.Expression):
                    return self.swap_slices(field)
                return swap_field(field)

            fieldset.rhs = branch(fieldset.rhs)
            fieldset.lhs = branch(fieldset.lhs)

            return fieldset

        # JOIN
        elif isinstance(fieldset, dict):
            for k, exs in fieldset.items():
                for m, ex in enumerate(exs):
                    self.swap_slices(ex.on)
        # DEBUG
        else:
            pdb.set_trace()

    # @common.debug_result
    def sql(self):
        self.swap_slices(self._select)
        self.swap_slices(self._where)
        self.swap_slices(self._joins)
        self.swap_slices(self._group_by)

        sql, params = super().sql()

        # common.print_query((sql, params)); print("\n")
        return sql, params

    @peewee.returns_clone
    def group_all(self):
        group = []
        for s in self._select:
            if isinstance(s, peewee.Func): continue
            s = s.clone()
            s._alias = ''
            group.append(s)

        self._group_by = self._model_shorthand(group)

    def slice(self, *args, **kwargs):
        cls = kwargs.get('cls')
        period = kwargs.get('period')
        on = kwargs.get('on')
        alias = kwargs.get('alias')
        date = kwargs.get('date')
        join_type = kwargs.get('join_type', peewee.JOIN.LEFT_OUTER)

        if cls is None:
            for arg in args:
                cls = arg.model_class
                break

        if period is None:
            period = cls.period

        if alias is None:
            alias = cls.__name__

        # ищем максимальный по полю period
        sub = (cls.select(*args, peewee.fn.MAX(period).alias(cls.__name__ + '_MAXPERIOD'), local = False)
               .group_by(*args)
               .alias(cls.__name__ + '_sub')
               )
        if (date):
            sub = sub.where(period > date)

        exs = peewee.Expression(period, peewee.OP.EQ, getattr(sub.c, cls.__name__ + '_MAXPERIOD'))
        for arg in args:
            if arg:
                ex = peewee.Expression(
                    getattr(cls, arg.name), peewee.OP.EQ,
                    getattr(sub.c, arg.db_column)
                    )
                exs &= ex

        slice_ = cls.select(cls, local = False).join(sub, on=(exs)).alias(cls.__name__)

        if alias:
            self.slice_aliases[alias] = (cls, slice_.c)

        def through_ex(ex):
            def branch(field):
                if isinstance(field, peewee.Expression):
                    field = through_ex(field)

                elif issubclass(type(field), peewee.Field) and cls == field.model_class:
                        return getattr(slice_.c, field.db_column)
                return field

            ex.rhs = branch(ex.rhs)
            ex.lhs = branch(ex.lhs)

            return ex
            

        on = through_ex(on)

        res = self.join(slice_, join_type=join_type, on=(on))

        return res


    # def _execute(self):
    #     # debug.log_info(hex(id(self)), self.local and "LOCAL" or "Legacy", self.model_class)
    #     if self.local:
    #         self.database = self.model_class._meta.database 
    #         self.require_commit = False
    #         try:
    #             cursor = super()._execute()
    #             return cursor
    #         except (peewee.OperationalError, sqlite3.OperationalError) as e:
    #             estr = e.args[0]
    #             param = None
    #             if estr.find(':'):
    #                 estr, param = estr.split(':')

    #             if estr == 'no such table':
    #                 for table in self._joins:
    #                     if table.table_exists():
    #                         continue

    #                     if issubclass(table, OnesEnum):
    #                         db_column = table.order.db_column
    #                         table.order.db_column = 'Представление'
    #                         table.order.null = True

    #                     debug.log_warning("Создаем таблицу в кеше", table._meta.db_table)
    #                     try:
    #                         table.create_table(fail_silently = False)
    #                     except (peewee.OperationalError, sqlite3.OperationalError) as e:
    #                         # pdb.set_trace()
    #                         debug.log_warning("Ошибка при создании таблицы", table._meta.db_table, e)

    #                     if issubclass(table, OnesEnum):
    #                         table.order.db_column = db_column

    #                 self.local = False
    #                 return self._execute()
    #     else:
    #         self.database = self.model_class._meta.legacy_db
    #         return super()._execute()

def save_queue():
    global unsaved 
    unsaved = set()
    while True:
        if unsaved:
            local = set(unsaved)
            print("Unsaved queue len", len(unsaved))
            print("Processing ", end='', flush=True)
            unsaved.clear()
            for el in local:
                print(".", end='', flush=True)
                # if issubclass(type(el), OnesEnum):
                el.cached = True
                el.save(recursive = True)
            print(" OK")
        else:
            time.sleep(2)
            # print("Empty queue")

# threading.Thread(name = "Save Queue", target = save_queue).start()

class OnesCore(peewee.Model):
    # table = peewee.CharField(db_column = '_ИмяТаблицы', max_length = 100, null = True)

    class Meta:
        # legacy_db = LegacyDatabase(sql_base, 
        database = LegacyDatabase(SQL_BASE, 
            host = SQL_HOST,
            user = SQL_USER,
            password = SQL_PASS, 
            appname = "External Record Log"
        )


        primary_key = False
        # database = LocalDatabase('/tmp/test.db')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached = True

    def prepare_local_db(self):
        for k, field in self._meta.fields.items():
            if isinstance(field, ForeignKey):
                el = getattr(self, k)
                if el is not None:
                    # print("unsaved.add(%s)" % el)
                    unsaved.add(el)
                    # el.save()
                    # print(el, type(el))

    def save(self, force_insert = False, recursive = True):
        return # important if legacy
        cls = type(self)
        try:
            # local only
            exist = cls.select().where(cls.ref == self.ref).get()
        except peewee.DoesNotExist as e:
            self.prepare_local_db()
            # if issubclass(type(self), OnesEnum):
            super().save(force_insert = True)

    def __str__(self):
        return self.table or self.__class__.__name__ + ": has NO name"

    @classmethod
    def warm_up(cls, query=None):
        if not cls.table_exists():
            cls.create_table(fail_silently = False)

        if query is None:
            res = cls.select(local = False) # for begin check local cache?
        else:
            res = query

        for row in list(res):
            if res.local:
                print("local", row)
                continue
                # break
            if row:
                # print("unsaved.add(%s)" % row)
                unsaved.add(row)

    @classmethod
    def select(cls, *selection, **kwargs):
        local = kwargs.pop('local', None)
        if local is None:
            query = peewee.SelectQuery(cls, *selection, **kwargs)
        else:
            query = SelectQuery(cls, *selection, **kwargs)
            query.local = local

        if cls._meta.order_by:
            query = query.order_by(*cls._meta.order_by)

        return query

    @classmethod
    def get(cls, *args, **kwargs):

        local = kwargs.pop('local', None) # if true => using local cache
        sq = cls.select(local = local).naive()

        try:
            if args:
                sq = sq.where(*args)
            if kwargs:
                sq = sq.filter(**kwargs)

            result = sq.get()

            if local is False:
                result.cached = False
                # print('В очереди на сохранение', result)
                unsaved.add(result)
                
            return result

        except peewee.DoesNotExist as e:
            if local is True:
                return cls.get(local = False)
            else:
                return cls()

    @classmethod
    def alias(cls):
        return ModelAlias(cls)



class OnesBase(OnesCore):
    ref = LinkField()
    ref_db = LinkFieldDB()
    ref_ones = LinkFieldOneS()

    def __bool__(self):
        return self.ref and True or False

    @classmethod
    def warm_up(cls, query=None):
        super(OnesBase, cls).warm_up(query = cls.select().order_by(cls.ref).limit(1000))

class OnesEnum(OnesBase):
    order = peewee.IntegerField(db_column = "Порядок")
    values = []

    def __str__(self):
        if isinstance(self.name, str):
            return self.name 

        return self.order or self.__class__.__name__ + ": has NO name"


class OnesRef(OnesBase):
    mark = BoolField(db_column = 'ПометкаУдаления', inverted = False)
    code = peewee.CharField(db_column = 'Код', max_length = 10)
    name = peewee.CharField(db_column = 'Наименование', max_length = 100)

    def __str__(self):
        return self.name or self.ref or self.__class__.__name__ + ": has NO name"

class OnesBP(OnesBase):
    date = DateField()
    mark = BoolField(db_column = 'ПометкаУдаления', inverted = False)
    number = peewee.CharField(db_column = 'Номер', max_length = 10)
    completed = BoolField(db_column='Завершен')
    started = BoolField(db_column='Стартован')

    def __str__(self):
        return self.name or self.ref or self.__class__.__name__ + ": has NO name"

class OnesPointRouteBP(OnesBase):
    order = peewee.IntegerField(db_column = "Порядок")

    def __str__(self):
        return self.name or self.ref or self.__class__.__name__ + ": has NO name"


class OnesTask(OnesBase):
    mark = BoolField(db_column = 'ПометкаУдаления', inverted = False)
    name = peewee.CharField(db_column = 'Наименование', max_length = 100)
    date = DateField()
    completed = BoolField(db_column = 'Выполнена')

    def __str__(self):
        return self.name or self.ref or self.__class__.__name__ + ": has NO name"


class OnesDoc(OnesBase):
    mark = BoolField(db_column = 'ПометкаУдаления', inverted = False)
    number = peewee.CharField(db_column = 'Номер', max_length = 10)
    # prefix = peewee.CharField(db_column="_NumberPrefix", max_length = 3)
    # name = peewee.CharField(db_column = '_ИмяТаблицы', max_length = 100)
    date = DateField()
    posted = BoolField(db_column = 'Проведен')

    def __str__(self):
        return self.table + ' №' + self.number + ' от ' + self.date.strftime("%d.%m.%Y")


class OnesTable(OnesBase):
    key = peewee.BlobField(db_column = '_KeyField')
    order = peewee.IntegerField(db_column = "НомерСтроки")
    # name = peewee.CharField(db_column = '_ИмяТаблицы', max_length = 100)

    class Meta:
        primary_key = peewee.CompositeKey('ref', 'key')
