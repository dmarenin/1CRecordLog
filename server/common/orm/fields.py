from datetime import datetime
import peewee, base64, binascii
import decimal

nullrefs = (
    b'00000000000000000000000000000000',
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    'NO REF!',
)

nulldate = datetime(2599, 1, 1, 0, 0)

class LinkField(peewee.BlobField):

    def __init__(self, *args, **kwargs):
        if not kwargs.get('primary_key'):
            kwargs['primary_key'] = True
        kwargs['db_column'] = 'Ссылка'
        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if value in nullrefs or value is None:
            return None

        return base64.b16encode(value).decode()

    def db_value(self, value):
        if value in nullrefs or value is None:
            return None

        try:
            return base64.b16decode(value.encode())
        except binascii.Error as e:
            return value

class LinkFieldDB(peewee.CharField):

    def __init__(self, *args, **kwargs):

        kwargs['db_column'] = '_ссылка_бд'
        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if value in nullrefs or value is None:
            return None

        return value

    def db_value(self, value):
        if value in nullrefs or value is None:
            return None
        
        return value

class LinkFieldOneS(peewee.CharField):


    def __init__(self, *args, **kwargs):

        kwargs['db_column'] = '_ссылка_'
        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if value in nullrefs or value is None:
            return None

        return value

    def db_value(self, value):
        if value in nullrefs or value is None:
            return None
        
        return value

        
class ForeignKey(LinkField, peewee.ForeignKeyField):

    def __init__(self, *args, **kwargs):
        peewee.ForeignKeyField.__init__(self, *args, **kwargs)


class DateField(peewee.DateTimeField):

    def __init__(self, *args, **kwargs):
        if not kwargs.get('db_column'):
            kwargs['db_column'] = 'Дата'
        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if value is None:
            return nulldate

        if isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

        return value.replace(year = value.year - 2000)

    def db_value(self, value):
        return value.replace(year = value.year + 2000)

    def timestamp(self):
        print(self._data)
        return 'AAA'

class BoolField(peewee.BooleanField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('inverted') is not None:
            self.inverted = (kwargs.get('inverted') is True)
            del kwargs['inverted']

        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if getattr(self, 'inverted', False):
            return True if value == b'\x00' else False
        else:
            return True if value == b'\x01' else False

    def db_value(self, value):
        if getattr(self, 'inverted', False):
            return 0x00 if value else 0x01
        else:
            return 0x01 if value else 0x00


class ENameKey(peewee.CharField):

    def __init__(self, values, *args, **kwargs):
        kwargs['db_column'] = "ПредставлениеЗначения"
        kwargs['max_length'] = 32
        super().__init__(*args, **kwargs)
        self.values = values

    # def python_value(self, value):
    #     if isinstance(value, (int, decimal.Decimal)):
    #         return self.values[int(value)]

    #     return value

    # def db_value(self, value):
    #     return self.values.index(value)

# отдельное поле из-за кривого порядка в конфигурации 1С
class ENameKeyTarget(ENameKey):
    pass

    # def python_value(self, value):
    #     if int(value) == 4:
    #         return self.values[3]
    #     elif int(value) == 3:
    #         return self.values[4]

    #     return self.values[int(value)]

    # def db_value(self, value):
    #     res = self.values.index(value)
    #     if res == 3: return 4
    #     elif res == 4: return 3
    #     return res

'''
 Поле для хранения ссылки на объект 1С
'''
class RefField(peewee.UUIDField):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.default = None
        self.null = True

    def db_value(self, value):
        return value.upper()


