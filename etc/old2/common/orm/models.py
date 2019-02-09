import peewee

if __name__ == '__main__':
    from base import OnesRef, OnesDoc, OnesEnum, OnesTable, OnesCore, OnesTask
    from fields import ForeignKey, BoolField, ENameKey, DateField, ENameKeyTarget
else:
    from .base import OnesRef, OnesDoc, OnesEnum, OnesTable, OnesCore, OnesTask
    from .fields import ForeignKey, BoolField, ENameKey, DateField, ENameKeyTarget

import common.orm.base as base
from common import common
from datetime import datetime


# region Перечисления

class Direction(OnesEnum):
    name = ENameKeyTarget([
        "Продажа",
        "Сервис",
        "Запчасти",
        "Прочее",
        "Кредит"
    ])

    class Meta:
        db_table = 'e_ВидДеятельности'

class ActivityStatus(OnesEnum):
    name = ENameKey([
        "Активен",
        "Не активен",
        "Телефон авторизован"
    ])

    class Meta:
        db_table = 'e_CRM_СтатусыАктивностиПользователей'

    def __str__(self):
        return self.name

class LogRecordKindWork(OnesEnum):
    name = ENameKey([
        "Прием",
        "Ремонт",
        "Выдача",
        "Обрудование"
    ])

    class Meta:
        db_table = 'e_ЖурналЗаписиВидРаботы'

    def __str__(self):
        return self.name

class JobMark(OnesEnum):
    name = ENameKey([
        "Часы8",
        "Часы5",
        "Больничный",
        "Выходной",
        "Отпуск",
        "Декрет",
        "Отгул",
        "Часы12",
        "Часы2",
        "Часы4",
        "Часы6",
        "Часы7",
        "Часы9",
        "Часы10",
        "Часы11",
        "Командировка",
        "Обучение"
    ])

    class Meta:
        db_table = 'e_ОтметкаОРаботе'

    def __str__(self):
        return self.name

    @staticmethod
    def getJobMarkWorkTime():
        return ['Часы8', 'Часы5', 'Часы12', 'Часы2', 'Часы4', 'Часы6', 'Часы7', 'Часы9', 'Часы10', 'Часы11']

class AdditionalCarInformation(OnesEnum):
    name = ENameKey([
        "Хозяин",
        "Пробег",
        "ГосНомер",
        "ТехПаспорт",
        "ВидАвтомобиля"

    ])

    class Meta:
        db_table = 'e_ДополнительнаяИнформацияАвтомобилей'

    def __str__(self):
        return self.name

class CRM_TypeEvent(OnesEnum):
    name = ENameKey([
        "Звонок",
        "Визит",
        "Email",
        "ПоисковыйЗвонок",
        "ПоисковыйВизит",
        "ЭлектроннаяОчередь"

    ])

    class Meta:
        db_table = 'e_CRM_ТипСобытия'

    def __str__(self):
        return self.name

class Area(OnesEnum):
    name = ENameKey([
        "Республики",
        "Федюнинского",
        "Сургут",
        "Червишевский",
        "Московский",
        "Дружба",
        "Щербакова"

    ])

    class Meta:
        db_table = 'e_Площадка'

    def __str__(self):
        return self.name

class TypeContactInfo(OnesEnum):
    name = ENameKey([
        "Адрес",
        "Телефон",
        "АдресЭлектроннойПочты",
        "ВебСтраница",
        "НомерICQ",
        "Другое"

    ])

    class Meta:
        db_table = 'e_ТипыКонтактнойИнформации'

    def __str__(self):
        return self.name

class KindsShedule(OnesEnum):
    name = ENameKey([
        "ЗонаПриема",
        "ЗонаРемонта",
        "НеОтображать",
        "ЗонаОбзвона"

    ])

    class Meta:
        db_table = 'e_РежимыРаботыСотрудниковЖЭЗ'

    def __str__(self):
        return self.name

# endregion


# region Справочники

class Org(OnesRef):
    class Meta:
        db_table = 'r_Организации'

class CarsBrand(OnesRef):
    class Meta:
        db_table = 'r_АвтомобильныеБренды'

class Brand(OnesRef):
    abrand =  ForeignKey(CarsBrand, db_column='АвтомобильныйБренд', related_name='brands', null = True)

    class Meta:
        db_table = 'r_Бренды'

class Dep(OnesRef):
    area = ForeignKey(Area, db_column='Площадка', null = True)
    brand = ForeignKey(Brand, db_column='Бренд', null = True)
    org = ForeignKey(Org, db_column='Организация')
    direction = ForeignKey(Direction, db_column='НаправлениеДеятельности', null = True)

    class Meta:
        db_table = 'r_ПодразделенияКомпании'

class Workshop(OnesRef):
    org = ForeignKey(Org, db_column='Организация')
    dep = ForeignKey(Dep, db_column='Подразделение')

    class Meta:
        db_table = 'r_Цеха'

class OrgCRM(OnesRef):
    show = BoolField(db_column='ОтображатьВКолЦентре')
    order = peewee.IntegerField(db_column='Приоритет')
    org = ForeignKey(Org, db_column='Владелец')

    class Meta:
        db_table = 'r_CRM_Организации'

class DepCRM(OnesRef):
    orgCrm = ForeignKey(OrgCRM, db_column='ОрганизацияCRM', related_name='deps', null = True)
    direction = ForeignKey(Direction, db_column='НаправлениеДеятельности', related_name='deps', null = True)
    phone = peewee.CharField(db_column='Телефоны', max_length=100)
    phoneExt = peewee.CharField(db_column='ТелефоныВнешние', max_length=100)
    show = BoolField(db_column='ОтображатьВCRM')

    class Meta:
        db_table = 'r_CRM_Подразделения'

    def managers(self):
        pass

class DepCRM_deps(OnesTable):
    link = ForeignKey(DepCRM, db_column='Ссылка', related_name='deps')
    dep = ForeignKey(Dep, db_column='Подразделение', related_name='linked_deps')

    class Meta:
        db_table = 'r_CRM_Подразделения_ПодразделенияКомпании'

class Positions(OnesRef):
    class Meta:
        db_table = 'r_Должности'

class Employee(OnesRef):
    fired = BoolField(db_column='ФлагУволен')
    cell = peewee.CharField(db_column='Телефон')
    phone = peewee.CharField(db_column='ТелефонВнутренний')
    position = ForeignKey(Positions, db_column='Должность')
    dep = ForeignKey(Dep, db_column='Подразделение', related_name='employees')
    is_expert_akr = BoolField(db_column='ЯвляетсяЭкспертомАКР')
    
    class Meta:
        db_table = 'r_Сотрудники'

class User(OnesRef):
    org = ForeignKey(Org, db_column='Организация', related_name='users')
    dep = ForeignKey(Dep, db_column='Подразделение', related_name='users')
    show = BoolField(db_column='ОтображатьВCRM')
    employee = ForeignKey(Employee, db_column='Сотрудник', related_name='users')
    template = ForeignKey('self', db_column='ШаблонПрав', related_name='users')

    class Meta:
        db_table = 'r_Пользователи'

class User_sub(OnesCore):
    main = ForeignKey(User, db_column='ПользовательОсновной')
    sub = ForeignKey(User, db_column='ПользовательДубль', related_name='linked_users')

    class Meta:
        db_table = 's_Пользователи'

class Contragent(OnesRef):
    phones = peewee.CharField(db_column='Телефоны')
    cellular = peewee.CharField(db_column='Сотовый', max_length=20)
    secondname = peewee.CharField(db_column='Фамилия')
    firstname = peewee.CharField(db_column='Имя')
    thname = peewee.CharField(db_column='Отчество')
    pol = ForeignKey(OnesRef, db_column='Пол', related_name='pol')
    urname = peewee.CharField(db_column='НаименованиеПолное')
    urinn = peewee.CharField(db_column='ИНН')
    urkpp = peewee.CharField(db_column='КПП')

    class Meta:
        db_table = 'r_Контрагенты'

    def save(self, force_insert = False, recursive = True):
        peewee.Model.save(self)

class Models(OnesRef):
    fullName = peewee.CharField(db_column='НаименованиеПолное')
    brand =  ForeignKey(CarsBrand, db_column='АвтомобильныйБренд', related_name='models', null = True)
    isgroup = BoolField(db_column='ЭтоГруппа')
    parent = ForeignKey(OnesRef, db_column='Родитель', related_name='parent')
    class Meta:
        db_table = 'r_Модели'

class Cars(OnesRef):
    vin = peewee.CharField(db_column='vin', max_length=24)
    vin2 = peewee.CharField(db_column='vin2', max_length=24)
    model = ForeignKey(Models, db_column='Модель')

    class Meta:
        db_table = 'r_Автомобили'

class RecallCars(OnesCore):
    vin = peewee.CharField(db_column='vin', max_length=24)
    campaign = peewee.CharField(db_column='Кампания', max_length=100)
    start = DateField(db_column="ДатаНачала")
    finish = DateField(db_column="ДатаОкончания")
    actual = BoolField(db_column="НеАктивна", inverted=True)
    status = BoolField(db_column="Статус")
    counter = peewee.IntegerField(db_column='КоличествоВыполнений')

    class Meta:
        db_table = 's_СервисныеКампании'

class ClientsCRM(OnesRef):
    primaryPhone = peewee.CharField(db_column='ОсновнойТелефон', max_length=100)
    contragent = ForeignKey(Contragent, db_column='Контрагент')
    car = ForeignKey(Cars, db_column='Автомобиль_ссылка')
    carStr = peewee.CharField(db_column='Автомобиль_строка', max_length=100)

    class Meta:
        db_table = 'r_CRM_Клиенты'

    def save(self, force_insert = False, recursive = True):
        peewee.Model.save(self)

class KindRepairCategory(OnesEnum):
    name = ENameKey([])

    class Meta:
        db_table = 'e_КатегорииВидовРемонта'

class KindRepair(OnesRef):
    category = ForeignKey(KindRepairCategory, db_column='Категория')
    class Meta:
        db_table = 'r_ВидыРемонта'

class CRM_Promises(OnesRef):
    comment = peewee.CharField(db_column='Комментарий', max_length=300)

    class Meta:
        db_table = 'r_CRM_Обещания'

class CRM_Services(OnesRef):
    class Meta:
        db_table = 'r_CRM_Услуги'

class CRM_Objections(OnesRef):
    answer = peewee.CharField(db_column='ОтветНаВозражение', max_length=256)

    class Meta:
        db_table = 'r_CRM_Возражения'

class CRM_Stocks(OnesRef):
    class Meta:
        db_table = 'r_CRM_Акции'

class CRM_ScriptsTalk(OnesRef):
    comment = peewee.CharField(db_column='Комментарий', max_length=256)
    variant = peewee.IntegerField(db_column='Вариант')

    class Meta:
        db_table = 'r_CRM_СкриптыРазговора'

class CRM_SpecOffers(OnesRef):
    comment = peewee.CharField(db_column='Комментарий', max_length=256)

    class Meta:
        db_table = 'r_CRM_Спецпредложения'

class CharSettingRecordLog(OnesRef):

    class Meta:
        db_table = 'ХарактеристикиНастройкиЖурналаЗаписи'

class WorkshopEquipment(OnesRef):
    class Meta:
        db_table = 'r_ОборудованиеЦеха'       

class Services(OnesRef):

    class Meta:
        db_table = 'r_Автоработы'

# endregion

class EventKinds(OnesEnum):
    name = peewee.CharField(db_column='ПредставлениеЗначения', max_length=32)

    class Meta:
        db_table = 'e_CRM_ТипСобытия'

# region Документы
class Event(OnesDoc):
    author = ForeignKey(User, db_column='Автор', related_name='events_author')
    manager = ForeignKey(User, db_column='Менеджер', related_name='events_manager')
    freelanceSituation = BoolField(db_column='ВнештатнаяСитуация')
    client = ForeignKey(ClientsCRM, db_column='Клиент', related_name='events_client')
    clientName = peewee.CharField(db_column='ИмяКлиента')
    phone = peewee.CharField(db_column='Телефон')
    dep = ForeignKey(Dep, db_column='Подразделение', related_name='events_dep')
    kind = ForeignKey(EventKinds, db_column='ТипСобытия', related_name='events')
    read = BoolField(db_column='Просмотрено')
    # task = ForeignKey(CRM_TasksService, db_column='Задача', related_name='events')

    class Meta:
        db_table = 'd_CRM_Событие'

    def save(self, force_insert = False, recursive = True):
        peewee.Model.save(self)

class OrderRepair(OnesDoc):
    car = ForeignKey(Cars, db_column='Автомобиль', related_name='carOrderOutfit')
    recommen = peewee.CharField(db_column='Рекомендации')
    dep = ForeignKey(Dep, db_column='ПодразделениеКомпании', related_name='Orders')

    class Meta:
        db_table = 'd_ЗаявкаНаРемонт'

class OrderOutfit(OnesDoc):
    car = ForeignKey(Cars, db_column='Автомобиль', related_name='carOrderRepair')
    recommen = peewee.CharField(db_column='Рекомендации')
    dep = ForeignKey(Dep, db_column='ПодразделениеКомпании', related_name='Queries')

    class Meta:
        db_table = 'd_ЗаказНаряд'


class RecordToLogRecord(OnesDoc):
    # buisnessProcessService = ForeignKey(CRM_BuisnessProcessService, db_column='БизнесПроцессСервис')
    dep = ForeignKey(Dep, db_column='ПодразделениеКомпании', related_name='records_to_log_record')
    kindRepair = ForeignKey(KindRepair, db_column='ВидРемонта')
    reason = peewee.CharField(db_column='ПричинаОбращения', max_length=150)

    contragent = ForeignKey(Contragent, db_column='Контрагент_ссылка')
    customer = ForeignKey(ClientsCRM, db_column='Заказчик_ссылка')
    phone = peewee.CharField(db_column='Телефон', max_length=10)

    car = ForeignKey(Cars, db_column='Автомобиль_ссылка', related_name='car_DocRec')
    carStr = peewee.CharField(db_column='Автомобиль_строка', max_length=50)
    carNumber = peewee.CharField(db_column='ГосНомер', max_length=10)

    orderRepair = ForeignKey(OrderRepair, db_column='ЗаявкаНаРемонт', related_name='orderRepairDocRec')
    orderOutfit = ForeignKey(OrderOutfit, db_column='ЗаказНаряд', related_name='orderOutfit_DocRec')
    
    notCome = BoolField(db_column='НеПриехал')
    author = ForeignKey(User, db_column='Автор')
    
    class Meta:
        db_table = 'd_ЗаписьВЖурналЗаписи'


class RecordToLogRecord_Promises(OnesTable):
    promise = ForeignKey(CRM_Promises, db_column='Обещание')
    link = ForeignKey(RecordToLogRecord, db_column='Ссылка')

    class Meta:
        db_table = 'd_ЗаписьВЖурналЗаписи_Обещания'


class RecordToLogRecord_Periods(OnesTable):
    ref = ForeignKey(RecordToLogRecord, db_column='Ссылка')

    kindWork = ForeignKey(LogRecordKindWork, db_column='ЖурналЗаписиВидРаботы')
    periodStart = DateField(db_column="ПериодНачало")
    periodEnd = DateField(db_column="ПериодОкончание")
    employee = ForeignKey(Employee, db_column='Сотрудник_ссылка')
    num_str = peewee.DecimalField(db_column="НомерСтроки") 
    key_periods_repair = peewee.CharField(db_column="КлючПериодаРемонта") 

    class Meta:
        db_table = 'd_ЗаписьВЖурналЗаписи_ПериодыРемонта'


class CertificatesOfControl(OnesDoc):
    car = ForeignKey(Cars, db_column='Автомобиль')

    class Meta:
        db_table = 'd_СертификатКонтроля'


class CertificatesOfControl_Diagnostics(OnesTable):
    rec_critical = BoolField(db_column='НемедленноУстранить')
    rec_normal = BoolField(db_column='Рекомендация')
    rec_good = BoolField(db_column='ВнешнеВпорядке')
    comment = peewee.CharField(db_column='Комментарий')
    exec_tag = BoolField(db_column='ОтметкаОВыполнении')

    link = ForeignKey(CertificatesOfControl, db_column='Ссылка')

    class Meta:
        db_table = 'd_СертификатКонтроля_Диагностика'


# endregion

# region Бизнес процессы

class CRM_BuisnessProcessService(OnesRef):
    out = BoolField(db_column='Аут')
    recordLR = ForeignKey(RecordToLogRecord, db_column='ЗаписьЖЗ')
    dep = ForeignKey(Dep, db_column='Подразделение')
    org = ForeignKey(Org, db_column='Организация')
    phone = peewee.CharField(db_column='Телефон', max_length=100)
    completed = BoolField(db_column='Завершен')
    started = BoolField(db_column='Стартован')
    car = ForeignKey(Cars, db_column='Автомобиль_ссылка', related_name='car_crm_bp_service')
    car_str = peewee.CharField(db_column='Автомобиль_строка')
    reason = peewee.CharField(db_column='ПричинаОбращения')
    comment = peewee.CharField(db_column='Комментарий')
    kindRepair = ForeignKey(KindRepair, db_column='ВидРемонта')
    dateLogService = DateField(db_column='ДатаЗаписиНаСервис')
    client = ForeignKey(ClientsCRM, db_column='Клиент')
    manager = ForeignKey(Employee, db_column='Мастер')

    class Meta:
        db_table = 'p_CRM_БизнесПроцессСервиса'

class ServiceRecord(OnesRef):
    recordLR = ForeignKey(RecordToLogRecord, db_column='ДокументЗаписи')
    completed = BoolField(db_column='Завершен')
    started = BoolField(db_column='Стартован')

    class Meta:
        db_table = 'p_ЗаписьНаСервис'

class ServiceRecord_Services(OnesTable):
    link = ForeignKey(ServiceRecord, db_column='Ссылка')
    service = ForeignKey(Services, db_column='Работа')
    #work_hour = peewee.DecimalField(db_column="НормоЧас") 
    #price = peewee.DecimalField(db_column="Цена") 
    amount = peewee.DecimalField(db_column="Количество") 
    work_hour = peewee.DecimalField(db_column="Коэффициент")
    #summ = peewee.DecimalField(db_column="Сумма") 
    #disc_summ = peewee.DecimalField(db_column="СуммаСкидки") 
    #disc_per = peewee.DecimalField(db_column="ПроцентСкидки")
    num_str = peewee.IntegerField(db_column='НомерСтроки')
    key_periods_repair = peewee.CharField(db_column="КлючПериодаРемонта") 

    class Meta:
        db_table = 'p_ЗаписьНаСервис_Работы'

# endregion

# region Точки бизнес процесса

class CRM_BuisnessProcessService_PointRoute(OnesEnum):
    name = peewee.CharField(db_column='ПредставлениеЗначения', max_length=40)

    class Meta:
        db_table = 'p_CRM_БизнесПроцессСервиса__Точки'

    def __str__(self):
        return self.name

    def type(self):
        if self.order == 4:
            return 'close'
        return 'unknown'

    @staticmethod
    def getPlannedPointRoute():
        return ["ЗапланированныйКонтакт", "ЗапланированныйКонтактОбзвона"]

    def get_type_client(var):

        if var == "Выдача автомобиля":
            return "close"


# endregion

# region Задачи

class CRM_TasksService(OnesTask):
    buisnessProcess = ForeignKey(CRM_BuisnessProcessService, db_column='БизнесПроцесс')
    pointRoute = ForeignKey(CRM_BuisnessProcessService_PointRoute, db_column='ТочкаМаршрута')
    noteByTask = peewee.CharField(db_column='ЗаметкаПоЗадаче', max_length=256)
    client = ForeignKey(ClientsCRM, db_column='Клиент')
    contragent = ForeignKey(Contragent, db_column='Контрагент')
    user = ForeignKey(User, db_column='Пользователь')
    dep = ForeignKey(Dep, db_column='ПодразделениеКомпании')
    employee = ForeignKey(Employee, db_column='Сотрудник')
    kindContact = ForeignKey(CRM_TypeEvent, db_column='ВидКонтакта')
    document = ForeignKey(Event, db_column='Документ', related_name='tasks')
    dateEnd = DateField(db_column='ДатаОкончания')
    dateNotify = DateField(db_column='ВремяНапоминания')
    position = ForeignKey(Positions, db_column='Должность')
    isNotActual = BoolField(db_column='НеСостоялась')
    completed = BoolField(db_column='Выполнена')

    class Meta:
        db_table = 't_CRM_ЗадачиСервиса'

# endregion

class PartsStatus(OnesEnum):
    name = ENameKey([])

    class Meta:
        db_table = 'e_СтатусыНоменклатуры'

class BP_Parts(base.OnesBP):
    contragent = ForeignKey(Contragent, db_column='Контрагент')
    dep = ForeignKey(Dep, db_column='Подразделение')
    status = ForeignKey(PartsStatus, db_column='Статус')
    out = BoolField(db_column='Аут')

    class Meta:
        db_table = 'p_ПродажаЗапчастей'

class point_Parts(OnesEnum):
    name = peewee.CharField(db_column='ПредставлениеЗначения', max_length=40)

    class Meta:
        db_table = 'p_ПродажаЗапчастей__Точки'

class task_Parts(base.OnesTask):
    bp = ForeignKey(BP_Parts, db_column='БизнесПроцесс')
    point = ForeignKey(point_Parts, db_column='ТочкаМаршрута')

    class Meta:
        db_table = 't_ЗадачиЗЧ'

# region План видов характеристик

class RightAndSetting(OnesRef):
    class Meta:
        db_table = 'c_ПраваИНастройки'

# endregion

# region Регистры сведений

class Staff_Work_Schedule(OnesCore):
    period = DateField(db_column="Период")
    employee = ForeignKey(Employee, db_column='Сотрудник')
    dep = ForeignKey(Dep, db_column='Подразделение')
    kindShedule = ForeignKey(KindsShedule, db_column='РежимыРаботыСотрудников')

    class Meta:
        db_table = 's_РежимыРаботыСотрудниковЖЭЗ'
        primary_key = peewee.CompositeKey('period', 'employee', 'dep', 'kindShedule')

    @classmethod
    def slice(cls, **kwargs):
        # res = (cls._slice(
        #     cls.dep,
        #     cls.employee,
        #     cls.period
        #     )
        # )
        # return res
        res = (Staff_Work_Schedule
            .select(Staff_Work_Schedule.dep.alias("dep"), Staff_Work_Schedule.employee.alias("employee"),
                    peewee.fn.MAX(Staff_Work_Schedule.period).alias('MAXPERIOD_'))

            .group_by(Staff_Work_Schedule.dep, Staff_Work_Schedule.employee)
            .alias("subquery"))

        if kwargs.get('dep'):
            res = res.where(Staff_Work_Schedule.dep == kwargs.get('dep'))

        res1 = (Staff_Work_Schedule
            .select(
                Staff_Work_Schedule.dep,
                Staff_Work_Schedule.employee,
                Staff_Work_Schedule.period,
                Staff_Work_Schedule.kindShedule,
                KindsShedule.name
                )
            .join(KindsShedule)
            .join(res, on=(
                (Staff_Work_Schedule.dep == res.c.dep) &
                (Staff_Work_Schedule.employee == res.c.employee) &
                (Staff_Work_Schedule.period == res.c.MAXPERIOD_)
                )
            )
        )

        if kwargs.get('kindsShedule'):
            res1 = res1.where(KindsShedule.name << kwargs.get('kindsShedule'))

        return res1

class CRM_AutoClients(OnesCore):
    client = ForeignKey(ClientsCRM, db_column='Клиент', related_name='client_autoClients')
    period = DateField(db_column="Период")
    car = ForeignKey(Cars, db_column='Автомобиль_ссылка', related_name='car_autoClients')
    car_str = peewee.CharField(db_column='Автомобиль_строка')
    isNotActual = BoolField(db_column='Продан')
    mileage = peewee.DecimalField(db_column='Пробег')
    yearOfIssue = DateField(db_column='ГодВыпуска')

    class Meta:
        db_table = 's_CRM_АвтомобилиКлиентов'

    @staticmethod
    def slice(**kwargs):

        res = (CRM_AutoClients
            .select(CRM_AutoClients.client.alias("client"), CRM_AutoClients.car.alias("car"),
                    CRM_AutoClients.car_str.alias("car_str"), peewee.fn.MAX(CRM_AutoClients.period).alias('MAXPERIOD_'))
            .group_by(CRM_AutoClients.client, CRM_AutoClients.car, CRM_AutoClients.car_str)
            .alias("subquery"))

        if kwargs.get('customer'):
            res = res.where(CRM_AutoClients.client == kwargs.get('customer'))

        res1 = (CRM_AutoClients
            .select(CRM_AutoClients.client, CRM_AutoClients.car, CRM_AutoClients.car_str,
                    CRM_AutoClients.isNotActual, CRM_AutoClients.mileage, CRM_AutoClients.yearOfIssue)

            .join(res,
                  on=((CRM_AutoClients.client == res.c.client) & (CRM_AutoClients.car == res.c.car) &
                      (CRM_AutoClients.car_str == res.c.car_str) & (CRM_AutoClients.period == res.c.MAXPERIOD_))))

        if kwargs.get('isNotActual') is not None:
            res1 = res1.where(CRM_AutoClients.isNotActual == kwargs.get('isNotActual'))

        return res1

class UserStatus(OnesCore):
    period = DateField(db_column="Период")
    user = ForeignKey(User, db_column="Пользователь", related_name="status")
    status = ForeignKey(ActivityStatus, db_column="Статус")
    comment = peewee.CharField(db_column='Комментарий', max_length=100)

    class Meta:
        db_table = 's_CRM_АктивностьПользователей'
        primary_key = False

    def save(self, force_insert = False, recursive = True):
        self.period = self.period.replace(microsecond=0)
        try:
            exist = (UserStatus
                    .update(status=self.status.ref)
                    .where(UserStatus.user == self.user)
                    .where(UserStatus.period == self.period)
                    .execute()
                )
            if exist:
                return
        except Exception as e:
            # print(e)
            pass

        peewee.Model.save(self) # , force_insert = True)

class RightsAndSettings(OnesCore):
    object = ForeignKey(OnesRef, db_column='Объект_ссылка', related_name='object_ras')
    settings = ForeignKey(RightAndSetting, db_column='ПравоНастройка', related_name='settings_ras')
    value_bool = BoolField(db_column='Значение')
    value_int = peewee.DecimalField(db_column='Значение_число')
    value_dt = DateField(db_column="Значение_тип")
    value_string = peewee.CharField(db_column='Значение_строка')
    value_ref = ForeignKey(OnesRef, db_column='Значение_ссылка', related_name='value_ref_ras')

    class Meta:
        db_table = 's_ПраваИНастройки'
        primary_key = False

class WorksheetKIA(OnesCore):
    period = DateField(db_column="Период")
    employee = ForeignKey(Employee, db_column='Сотрудник')
    position = ForeignKey(Positions, db_column='Должность')
    dep = ForeignKey(Dep, db_column='Подразделение')
    org = ForeignKey(Org, db_column='Организация')
    date = DateField(db_column="Дата")
    idRecord = ForeignKey(OnesRef, db_column='Регистратор')
    active = BoolField(db_column='Активность')
    numStr = peewee.IntegerField(db_column='НомерСтроки')
    mark = ForeignKey(JobMark, db_column='Отметка', related_name='mark_ws')

    class Meta:
        db_table = 's_ГрафикРаботыКИА'
        primary_key = False

    @staticmethod
    def slice(**kwargs):
        res = (WorksheetKIA
            .select(

            WorksheetKIA.org.alias("org"),
            WorksheetKIA.dep.alias("dep"),
            WorksheetKIA.employee.alias("employee"),
            WorksheetKIA.position.alias("position"),
            WorksheetKIA.date.alias("date"),
            peewee.fn.MAX(WorksheetKIA.period).alias('MAXPERIOD_')
        )

            .group_by(
            WorksheetKIA.org,
            WorksheetKIA.dep,
            WorksheetKIA.employee,
            WorksheetKIA.position,
            WorksheetKIA.date)

            .alias("subquery")

            )
        if kwargs.get('dates'):
            res = res.where(WorksheetKIA.date << kwargs.get('dates'))

        if kwargs.get('dep'):
            res = res.where(WorksheetKIA.dep == kwargs.get('dep'))

        if kwargs.get('employees'):
            res = res.where(WorksheetKIA.employee << kwargs.get('employees'))

        res1 = (WorksheetKIA
            .select(

            WorksheetKIA.org,
            WorksheetKIA.dep,
            WorksheetKIA.employee,
            WorksheetKIA.position,
            WorksheetKIA.date,
            WorksheetKIA.period,
            WorksheetKIA.mark,

            JobMark.name,

            Positions.ref.alias("postionRef"),
            Positions.name.alias("positionName"),

            Employee.name.alias("employeeName"),
            Employee.phone.alias("employeePhone")

        )

            .join(res, on=(
                (WorksheetKIA.org == res.c.org) &
                (WorksheetKIA.dep == res.c.dep) &
                (WorksheetKIA.employee == res.c.employee) &
                (WorksheetKIA.position == res.c.position) &
                (WorksheetKIA.date == res.c.date) &
                (WorksheetKIA.period == res.c.MAXPERIOD_)))

            .join(JobMark)

            .join(Positions, on=(
            (WorksheetKIA.position == Positions.ref)))

            .join(Employee, on=(
            (WorksheetKIA.employee == Employee.ref)))

            .order_by(WorksheetKIA.date)

            )

        if kwargs.get('marksWorkTime'):
            res1 = res1.where(JobMark.name << kwargs.get('marksWorkTime'))

        if kwargs.get('positionName'):
            res1 = res1.where(Positions.name == kwargs.get('positionName'))

        return res1

class LogRecordNew(OnesCore):
    period = DateField(db_column="Период")
    comment = peewee.CharField(db_column='Комментарий', max_length=150)
    dep = ForeignKey(Dep, db_column='Подразделение')
    periodStart = DateField(db_column="ПериодНачало")
    periodEnd = DateField(db_column="ПериодОкончание")
    employee = ForeignKey(Employee, db_column='Сотрудник')
    org = ForeignKey(Org, db_column='Организация')
    kindWork = ForeignKey(LogRecordKindWork, db_column='ЖурналЗаписиВидРаботы')
    kindRepair = ForeignKey(KindRepair, db_column='ВидРемонта')

    # region составные типы

    contragent = ForeignKey(Contragent, db_column='Контрагент_ссылка')
    contragentStr = peewee.CharField(db_column='Контрагент_строка', max_length=50)

    customer = ForeignKey(ClientsCRM, db_column='Заказчик_ссылка')
    customerStr = peewee.CharField(db_column='Заказчик_строка', max_length=100)

    car = ForeignKey(Cars, db_column='Автомобиль_ссылка', related_name='car_logRec')
    carStr = peewee.CharField(db_column='Автомобиль_строка', max_length=50)

    # endregion

    reason = peewee.CharField(db_column='ПричинаОбращения', max_length=150)
    phone = peewee.CharField(db_column='Телефон', max_length=10)
    carNumber = peewee.CharField(db_column='ГосНомер', max_length=10)

    idRecord = ForeignKey(RecordToLogRecord, db_column='Регистратор', related_name='idRecord_logRec')

    orderRepair = ForeignKey(OrderOutfit, db_column='ЗаявкаНаРемонт', related_name='orderRepairlogRec')
    orderOutfit = ForeignKey(OrderOutfit, db_column='ЗаказНаряд', related_name='orderOutfit_logRec')

    notCome = BoolField(db_column='НеПриехал')

    class Meta:
        db_table = 's_ЖурналЗаписиНовый'
        primary_key = False

    @staticmethod
    def slice(**kwargs):
        res = (LogRecordNew
            .select(
            LogRecordNew.periodStart.alias('periodStart'),
            LogRecordNew.periodEnd.alias('periodEnd'),
            LogRecordNew.contragent.alias('contragent'),
            LogRecordNew.contragentStr.alias('contragentStr'),
            LogRecordNew.kindWork.alias('kindWork'),
            LogRecordNew.dep.alias('dep'),
            LogRecordNew.org.alias('org'),
            LogRecordNew.employee.alias('employee'),
            LogRecordNew.customer.alias('customer'),
            LogRecordNew.customerStr.alias('customerStr'),
            LogRecordNew.car.alias('car'),
            LogRecordNew.carStr.alias('carStr'),

            peewee.fn.MAX(LogRecordNew.period).alias('MAXPERIOD_'),
        )

            .group_by(
            LogRecordNew.periodStart,
            LogRecordNew.periodEnd,
            LogRecordNew.contragent,
            LogRecordNew.contragentStr,
            LogRecordNew.kindWork,
            LogRecordNew.dep,
            LogRecordNew.org,
            LogRecordNew.employee,
            LogRecordNew.customer,
            LogRecordNew.customerStr,
            LogRecordNew.car,
            LogRecordNew.carStr,
            )

            .alias("subquery")

            )

        if kwargs.get('periodStart'):
            res = res.where(LogRecordNew.periodStart >= kwargs.get('periodStart'))

        if kwargs.get('periodEnd'):
            res = res.where(LogRecordNew.periodEnd <= kwargs.get('periodEnd'))

        if kwargs.get('dep'):
            res = res.where(LogRecordNew.dep == kwargs.get('dep'))

        if kwargs.get('employees'):
            res = res.where(LogRecordNew.employee << kwargs.get('employees'))

        if kwargs.get('r_ref'):
            res = res.where(LogRecordNew.idRecord == kwargs.get('r_ref'))

        res = res.where(LogRecordNew.notCome == False)

        res1 = (LogRecordNew
            .select(

            LogRecordNew.periodStart.alias("periodStart"),
            LogRecordNew.periodEnd.alias("periodEnd"),
            LogRecordNew.contragent.alias("contragent"),
            LogRecordNew.contragentStr.alias("contragentStr"),
            LogRecordNew.kindWork.alias("kindWork"),
            LogRecordNew.dep.alias("dep"),
            LogRecordNew.org.alias("org"),
            LogRecordNew.employee.alias("employee"),
            LogRecordNew.customer.alias("customer"),
            LogRecordNew.customerStr.alias("customerStr"),
            LogRecordNew.car.alias("car"),
            LogRecordNew.carStr.alias("carStr"),
            LogRecordNew.period.alias("period"),
            LogRecordNew.reason.alias("reason"),
            LogRecordNew.phone.alias("phone"),
            LogRecordNew.carNumber.alias("carNumber"),
            LogRecordNew.idRecord.alias("idRecord"),
            LogRecordNew.orderOutfit.alias("orderOutfit"),
            LogRecordNew.orderRepair.alias("orderRepair"),

            CRM_BuisnessProcessService.ref.alias("idBuisnessProcess"),
            CRM_BuisnessProcessService.completed.alias("buisnessProcessCompleted"),

            Contragent.name.alias("contragentName"),

            ClientsCRM.name.alias("customerName"),

            Cars.name.alias("carsName"),

            Models.name.alias("modelsName"),

            Employee.name.alias("employeeName"),

            RecordToLogRecord.orderOutfit.alias("orderOutfit"),
            RecordToLogRecord.orderRepair.alias("orderForRepair"),

            KindRepair.name.alias("kindRepair")

        )

            .join(res, on=(
                (LogRecordNew.periodStart == res.c.periodStart) &
                (LogRecordNew.periodEnd == res.c.periodEnd) &
                (LogRecordNew.contragent == res.c.contragent) &
                (LogRecordNew.contragentStr == res.c.contragentStr) &
                (LogRecordNew.kindWork == res.c.kindWork) &
                (LogRecordNew.dep == res.c.dep) &
                (LogRecordNew.org == res.c.org) &
                (LogRecordNew.employee == res.c.employee) &
                (LogRecordNew.customer == res.c.customer) &
                (LogRecordNew.customerStr == res.c.customerStr) &
                (LogRecordNew.car == res.c.car) &
                (LogRecordNew.carStr == res.c.carStr) &
                (LogRecordNew.period == res.c.MAXPERIOD_)))

            .join(CRM_BuisnessProcessService, join_type=peewee.JOIN.LEFT_OUTER, on=(
            (LogRecordNew.idRecord == CRM_BuisnessProcessService.recordLR)))

            .join(RecordToLogRecord, on=(
            (LogRecordNew.idRecord == RecordToLogRecord.ref)))

            .join(Contragent, join_type=peewee.JOIN.LEFT_OUTER, on=(
                LogRecordNew.contragent == Contragent.ref))

            .join(ClientsCRM, join_type=peewee.JOIN.LEFT_OUTER, on=(
                LogRecordNew.customer == ClientsCRM.ref))

            .join(Cars, join_type=peewee.JOIN.LEFT_OUTER, on=(
                LogRecordNew.car == Cars.ref))

            .join(Models, join_type=peewee.JOIN.LEFT_OUTER, on=(
                LogRecordNew.car == Models.ref))

            .join(Employee, on=(
            (LogRecordNew.employee == Employee.ref)))

            .switch(RecordToLogRecord)

            .join(KindRepair, join_type=peewee.JOIN.LEFT_OUTER, on=(
                RecordToLogRecord.kindRepair == KindRepair.ref))

            .order_by(LogRecordNew.periodStart)

            )

        if kwargs.get('phone'):
            res1 = res1.where(LogRecordNew.phone.contains(kwargs.get('phone')))

        res1 = res1.dicts()

        return res1

class CarsCharacteristics(OnesCore):
    # period = DateField(db_column="_Period")
    # car = ForeignKey(Cars, db_column='_Fld2829RRef', related_name='car_char')
    # kindValue = ForeignKey(AdditionalCarInformation, db_column='_Fld2830RRef')

    # valueType= peewee.BlobField(db_column='_Fld2831_TYPE')
    # valueStr = peewee.CharField(db_column='_Fld2831_S', max_length=20)
    # valueInt = peewee.IntegerField(db_column='_Fld2831_N')
    # valueRef = ForeignKey(OnesRef, db_column='_Fld2831_RRRef', related_name='valRef_char')

    period = DateField(db_column="Период")
    car = ForeignKey(Cars, db_column='Автомобиль', related_name='car_char')
    kindValue = ForeignKey(AdditionalCarInformation, db_column='ВидЗначения')

    valueType= peewee.BlobField(db_column='Значение_типПоля')
    valueStr = peewee.CharField(db_column='Значение_строка', max_length=20)
    valueInt = peewee.IntegerField(db_column='Значение_число')
    valueRef = ForeignKey(OnesRef, db_column='Значение_ссылка', related_name='valRef_char')

    class Meta:
        # db_table = '_InfoRg2828'
        db_table = 's_Автомобили'
        primary_key = False
        
    def save(self, force_insert = False, recursive = True):
        if not self.period:
            self.period = datetime.now().date()
        peewee.Model.save(self)

    @staticmethod
    def slice(**kwargs):

        res = (CarsCharacteristics
            .select(

            CarsCharacteristics.kindValue.alias('kindValue'),
            CarsCharacteristics.car.alias('car'),

            peewee.fn.MAX(CarsCharacteristics.period).alias('MAXPERIOD_')

        )
            .join(Cars, on=(CarsCharacteristics.car == Cars.ref))
            .group_by(
            CarsCharacteristics.kindValue,
            CarsCharacteristics.car
        )

            .alias("subquery")

            )

        if kwargs.get('period') is not None:
            res = res.where(CarsCharacteristics.period <= (kwargs.get('period')))

        if kwargs.get('car') is not None:
            res = res.where(CarsCharacteristics.car == (kwargs.get('car')))

        if kwargs.get('vin') is not None:
            res = res.where(Cars.vin.contains(kwargs.get('vin')) or Cars.vin2.contains(kwargs.get('vin')))

        res1 = (CarsCharacteristics
            .select(

            CarsCharacteristics.kindValue,
            CarsCharacteristics.valueStr,
            CarsCharacteristics.valueRef,
            CarsCharacteristics.valueInt,
            AdditionalCarInformation.name,
            Cars.name.alias("carName"),
            Cars.ref,
            Cars.vin,
            Cars.vin2

        )
            .join(AdditionalCarInformation)

            .join(Cars, on=(CarsCharacteristics.car == Cars.ref))

            .join(res, on=(
                (CarsCharacteristics.kindValue == res.c.kindValue) &
                (CarsCharacteristics.period == res.c.MAXPERIOD_) &
                (CarsCharacteristics.car == res.c.car)))
            .order_by(Cars.name.asc()))

        if kwargs.get('contragent') is not None:
            res1 = res1.where(CarsCharacteristics.valueRef == (kwargs.get('contragent')))
            res1 = res1.where(AdditionalCarInformation.name == 'Хозяин')

        if kwargs.get('number') is not None:
            res1 = res1.where(CarsCharacteristics.valueStr.contains(kwargs.get('number')))
            res1 = res1.where(AdditionalCarInformation.name == 'ГосНомер')

        if kwargs.get('notActualCars') is not None:
            if len(kwargs.get('notActualCars'))>0:
                res1 = res1.where(CarsCharacteristics.car.not_in((kwargs.get('notActualCars'))))

        return res1

class ContactInformation(OnesCore):
    period = DateField(db_column="Период")
    object = ForeignKey(OnesRef, db_column='Объект_ссылка')
    objectType = peewee.BlobField(db_column='Объект_типПоля')
    objectRType = peewee.BlobField(db_column='Объект_типСсылки')
    type = ForeignKey(TypeContactInfo, db_column='Тип')
    phone = peewee.CharField(db_column='Телефон', max_length=10)
    view = peewee.CharField(db_column='Представление', max_length=256)
    comment = peewee.CharField(db_column='Комментарий', max_length=256)
    notActual = BoolField(db_column='НеАктуально')
    hidden = BoolField(db_column='Скрытый')
    date = DateField(db_column="Дата")
    user = ForeignKey(User, db_column='Пользователь')

    class Meta:
        db_table = 's_КонтактнаяИнформация'
        primary_key = False

    def save(self, force_insert = False, recursive = True):
        if not self.period:
            self.period = datetime.now().replace(microsecond=0)
        if not self.date:
            self.date = datetime.now().replace(microsecond=0)
        peewee.Model.save(self)

    @staticmethod
    def slice(**kwargs):

        res = (ContactInformation
            .select(

            ContactInformation.object.alias("object"),
            ContactInformation.type.alias("type"),
            ContactInformation.phone.alias("phone"),
            peewee.fn.MAX(ContactInformation.period).alias('MAXPERIOD_')
        )

            .group_by(
            ContactInformation.object,
            ContactInformation.type,
            ContactInformation.phone)

            .alias("subquery")

            )
        if kwargs.get('phone'):
            res = res.where(ContactInformation.phone.contains(kwargs.get('phone')))

        if kwargs.get('object'):
            res = res.where(ContactInformation.object == kwargs.get('object'))

        res1 = (ContactInformation
            .select(

            ContactInformation.object.alias("object"),
            ContactInformation.type.alias("type"),
            ContactInformation.phone.alias("phone"),
            ContactInformation.period.alias("period"),

            # ContactInformation.view.alias("view"),
            ContactInformation.comment.alias("comment"),
            ContactInformation.notActual.alias("notActual"),
            ContactInformation.hidden.alias("hidden"),
            # ContactInformation.date.alias("date")
            # ContactInformation.user.alias("user")

        )

            .join(res, on=(
                (ContactInformation.object == res.c.object) &
                (ContactInformation.type == res.c.type) &
                (ContactInformation.phone == res.c.phone) &
                (ContactInformation.period == res.c.MAXPERIOD_)))

            .order_by(ContactInformation.period)

            )

        if kwargs.get('hidden') is not None:
            res1 = res1.where(ContactInformation.hidden == kwargs.get('hidden'))

        if kwargs.get('notActual') is not None:
            res1 = res1.where(ContactInformation.notActual == kwargs.get('notActual'))

        if kwargs.get('periodStart'):
            res1 = res1.where(ContactInformation.period >= kwargs.get('periodStart'))

        if kwargs.get('periodEnd'):
            res1 = res1.where(ContactInformation.period <= kwargs.get('periodEnd'))

        return res1

class CRM_СlientsContragents(OnesCore):
    client = ForeignKey(ClientsCRM, db_column='Клиент')
    contragent = ForeignKey(Contragent, db_column='Контрагент')

    class Meta:
        db_table = 's_CRM_КлиентыКонтрагентов'
        primary_key = False

class CRM_PriceService(OnesCore):
    period = DateField(db_column="Период")
    crm_service = ForeignKey(CRM_Services, db_column='CRM_Услуга')
    org = ForeignKey(Org, db_column='Организация')
    dep = ForeignKey(Dep, db_column='Подразделение')
    model = ForeignKey(Models, db_column='Модель')
    brand = ForeignKey(CarsBrand, db_column='Бренд')
    price = peewee.IntegerField(db_column='Цена')
    quantityWH = peewee.IntegerField(db_column='КоличествоНЧ')

    class Meta:
        db_table = 's_CRM_ЦеныУслуг'

    @staticmethod
    def slice(**kwargs):
        res = (CRM_PriceService
            .select(

            CRM_PriceService.crm_service.alias('crm_service'),
            # CRM_PriceService.org.alias('org'),
            # CRM_PriceService.dep.alias('dep'),
            # CRM_PriceService.model.alias('model'),
            # CRM_PriceService.brand.alias('brand'),
            peewee.fn.MAX(CRM_PriceService.period).alias('MAXPERIOD_')
        )

            .group_by(
            CRM_PriceService.crm_service,
            # CRM_PriceService.org,
            # CRM_PriceService.dep,
            # CRM_PriceService.model,
            # CRM_PriceService.brand
        )
            .alias("subquery")

            )

        res1 = (CRM_PriceService
            .select(

            CRM_PriceService.crm_service,
            # CRM_PriceService.org,
            # CRM_PriceService.dep,
            # CRM_PriceService.model,
            # CRM_PriceService.brand,
            # CRM_PriceService.price,
            peewee.fn.MAX(CRM_PriceService.price).alias('priceMAX'),
            peewee.fn.MIN(CRM_PriceService.price).alias('priceMIN'),
            peewee.fn.MAX(CRM_PriceService.quantityWH).alias('quantityWHMAX'),
            peewee.fn.MIN(CRM_PriceService.quantityWH).alias('quantityWHMIN'),
            CRM_Services.name.alias("crm_service_name")

        )
            .join(CRM_Services)
            .join(res, on=(
                (CRM_PriceService.crm_service == res.c.crm_service) &
                # (CRM_PriceService.org == res.c.org) &
                # (CRM_PriceService.dep == res.c.dep) &
                # (CRM_PriceService.model == res.c.model) &
                # (CRM_PriceService.brand == res.c.brand) &
                (CRM_PriceService.period == res.c.MAXPERIOD_)))
            .group_by(
            CRM_PriceService.crm_service,
            # CRM_PriceService.org,
            # CRM_PriceService.dep,
            # CRM_PriceService.model,
            # CRM_PriceService.brand
            CRM_Services.name
        )
        )

        if kwargs.get('model') is not None:
            res1 = res1.where((CRM_PriceService.model == kwargs.get('model')))

        return res1

class CRM_ValidityStocksPeriod(OnesCore):
    crm_stock = ForeignKey(CRM_Stocks, db_column='CRM_Акции')
    period = DateField(db_column="Период")
    periodStart = DateField(db_column="ПериодНачала")
    periodEnd = DateField(db_column="ПериодОкончания")

    class Meta:
        db_table = 's_CRM_СрокиДействияАкций'

    @staticmethod
    def slice(**kwargs):
        res = (CRM_ValidityStocksPeriod
            .select(

            CRM_ValidityStocksPeriod.crm_stock.alias('crm_stock'),
            peewee.fn.MAX(CRM_ValidityStocksPeriod.period).alias('MAXPERIOD_')

        )

            .group_by(
            CRM_ValidityStocksPeriod.crm_stock
        )
            .alias("subquery")

            )

        res1 = (CRM_ValidityStocksPeriod
            .select(

            CRM_ValidityStocksPeriod.crm_stock,
            CRM_ValidityStocksPeriod.periodEnd,
            CRM_ValidityStocksPeriod.periodStart,
            CRM_ValidityStocksPeriod.period

        )
            .join(res, on=(
                (CRM_ValidityStocksPeriod.crm_stock == res.c.crm_stock) &
                (CRM_ValidityStocksPeriod.period == res.c.MAXPERIOD_)))

            .order_by(CRM_ValidityStocksPeriod.periodStart)
            )

        if kwargs.get('periodStart') is not None:
            res1 = res1.where((CRM_ValidityStocksPeriod.periodStart >= kwargs.get('periodStart')) |
                              (CRM_ValidityStocksPeriod.periodEnd >= kwargs.get('periodStart')))

        return res1

class SettingsRecordLog(OnesCore):
    
    reg = peewee.CharField(db_column="Регистратор")

    period = DateField(db_column="Период")
    char = ForeignKey(CharSettingRecordLog, db_column='Характеристика')
    dep = ForeignKey(Dep, db_column='Подразделение')
    num_day = peewee.IntegerField(db_column='ДеньНедели')
   
    accept_proc =  peewee.IntegerField(db_column='ПроцентЗагрузки')
    accept_start = DateField(db_column="ЗагрузкаНачало")
    accept_end = DateField(db_column="ЗагрузкаОкончание")

    val_int = peewee.IntegerField(db_column='Знач_число')
    val_date = DateField(db_column="Знач_тип")
    val_str = peewee.CharField(db_column='Знач_строка', max_length=100)

    periodStart = DateField(db_column="ПериодНачало")
    periodEnd = DateField(db_column="ПериодОкончание")

    val_char = ForeignKey(WorkshopEquipment, db_column='ЗначениеХарактеристики')

    class Meta:
        db_table = 's_НастройкиЖурналаЗаписи'

    @staticmethod
    def slice(**kwargs):
        res = (SettingsRecordLog.select(peewee.fn.MAX(SettingsRecordLog.period).alias('MAXPERIOD_')))
           
        if kwargs.get('dep') is not None:
            res = res.where((SettingsRecordLog.dep == kwargs.get('dep')))
               
        if kwargs.get('char') is not None:
           res = res.where((SettingsRecordLog.char == kwargs.get('char')))

        res_list = list(res.dicts())

        if len(res_list) == 0:
            return []

        res1 = (SettingsRecordLog
            .select(
            SettingsRecordLog.char.alias('char'),
            SettingsRecordLog.dep.alias('dep'),
            
            SettingsRecordLog.num_day.alias('num_day'),
            SettingsRecordLog.accept_proc.alias('accept_proc'),
            SettingsRecordLog.accept_start.alias('accept_start'),
            SettingsRecordLog.accept_end.alias('accept_end'),

            SettingsRecordLog.val_int.alias('val_int'),
            SettingsRecordLog.val_date.alias('val_date'),
            SettingsRecordLog.val_str.alias('val_str'),
            SettingsRecordLog.val_char.alias('val_char'),
            SettingsRecordLog.period.alias('period'),
            SettingsRecordLog.reg,

            #peewee.fn.MAX(SettingsRecordLog.num_day).alias('num_day'),
            #peewee.fn.MAX(SettingsRecordLog.accept_proc).alias('accept_proc'),
            #peewee.fn.MAX(SettingsRecordLog.accept_start).alias('accept_start'),
            #peewee.fn.MAX(SettingsRecordLog.accept_end).alias('accept_end'),

            #peewee.fn.MAX(SettingsRecordLog.val_int).alias('val_int'),
            #peewee.fn.MAX(SettingsRecordLog.val_date).alias('val_date'),
            #peewee.fn.MAX(SettingsRecordLog.val_str).alias('val_str')

        ).distinct().where(SettingsRecordLog.period == res_list[0]['MAXPERIOD_']))
            #.join(res, on=(
            #    #(SettingsRecordLog.char == res.c.char) &
            #    #(SettingsRecordLog.dep == res.c.dep) &
            #    #(SettingsRecordLog.reg == res.c.reg) &
            #    #(SettingsRecordLog.val_char == res.c.val_char) &
            #    #(SettingsRecordLog.num_day == res.c.num_day) &
            #    #(SettingsRecordLog.accept_proc == res.c.accept_proc) &
            #    #(SettingsRecordLog.accept_start == res.c.accept_start) &
            #    #(SettingsRecordLog.accept_end == res.c.accept_end) &
            #    #(SettingsRecordLog.val_char == res.c.val_char) &
            #    (SettingsRecordLog.period == res_list[0]['MAXPERIOD_'])))

            ##.group_by(SettingsRecordLog.char,
            ##          SettingsRecordLog.dep)
        

        if kwargs.get('dep') is not None:
            res1 = res1.where((SettingsRecordLog.dep == kwargs.get('dep')))
               
        if kwargs.get('char') is not None:
           res1 = res1.where((SettingsRecordLog.char == kwargs.get('char')))

        return res1

# endregion

# region Регистры накопления

class CompanyCalculations(OnesCore):
    period = DateField(db_column="Период")
    sum = peewee.DecimalField(db_column="Сумма")
    deal = ForeignKey(OnesDoc, db_column='Сделка_ссылка')
    contragent = ForeignKey(Contragent, db_column='Контрагент')
    sign = peewee.IntegerField(db_column='ВидДвижения')
    dealBasis = ForeignKey(OnesDoc, db_column='СделкаДокументОснование_ссылка', related_name='dealBasis')

    class Meta:
        db_table = 'a_ВзаиморасчетыКомпании'

class EmployeeDevelopment(OnesCore):
    period = DateField(db_column="Период")
    employee = ForeignKey(Employee, db_column="Сотрудник")
    workshop = ForeignKey(Workshop, db_column="Цех")
    sum_upr = peewee.DecimalField(db_column="СуммаУпр")
    sum_upr_with_disc = peewee.DecimalField(db_column="СуммаУпрСоСкидкой")
    count = peewee.DecimalField(db_column="Количество")

    class Meta:
        db_table = 'a_ВыработкаСотрудников_Обороты'

# endregion

if __name__ == '__main__':
    sqlite = peewee.SqliteDatabase('test.db')

    class WriteModelOrg(peewee.Model):
        ref = peewee.CharField(db_column = 'Ссылка', max_length = 32, primary_key = True)
        table = peewee.CharField(db_column = 'Наименование', max_length = 100)

        class Meta:
            database = sqlite

    # sqlite.create_tables([WriteModelOrg])

    # res = LogRecordKindWork.select();
    
    local_res = WriteModelOrg.select().where(WriteModelOrg.ref == 'AF8E50505450303011DBD94C5E0EE55C')
    res = None

    if not local_res:
        res = Org.select().where(Org.ref == 'AF8E50505450303011DBD94C5E0EE55C')
        print(res.sql())
        for r in list(res):
            print(r) 

            org = WriteModelOrg.create(
                ref = r.ref,
                table = r.name
            )
            print(org)
            org.save()

    if local_res:
        print(list(local_res.dicts()))
    if res:
        print(list(res.dicts()))


