import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groupsw.settings')
import pandas as pd
import django
from faker import Faker
django.setup()
from appointment.models import Workdays, TimeSlot, Schedule, Person, Appointment, Sex
from datetime import datetime
fake = Faker()
from appointment.views import *
import random

csvfile = pd.read_csv('insurance.csv')


def createPerson():
    randomData = csvfile.sample()
    fullname = fake.name().split()
    first_name = fullname[0]
    last_name = fullname[1]
    adress = fake.address()
    amka = fake.random_number(digits=8)
    phone = fake.random_number(digits=10)
    sex = Sex.male if randomData['sex'].values[0] == "male" else Sex.female

    bmi = randomData['bmi'].values[0]
    smoker = True if randomData['smoker'].values[0] == "yes" else False
    children = randomData['children'].values[0]
    age = randomData['age'].values[0]

    person = Person.objects.get_or_create(first_name=first_name, last_name=last_name, sex=sex,
                                 address=adress, amka=amka, bmi=bmi,
                                 smoker=smoker, children=children, age=age, phone=phone)

    return person


def create_workday(day):
    Workdays.objects.get_or_create(date=day)


def workdays_seeder():
    days = pd.bdate_range(start='1/1/2019', end='12/31/2025')

    for day in days:
        print(day)
        create_workday(day)


def timeslot_seeder():
    for time in range(0, 8):
        TimeSlot.objects.get_or_create(start_time=time + 8, end_time= time + 9)


def schedule_seeder():
    workdays = Workdays.objects.all()
    timeslots = TimeSlot.objects.all()

    for workday in workdays:
        for timeslot in timeslots:
            Schedule.objects.create(workday=workday, timeslot=timeslot)


def appointments_seeder():
    startDate = datetime.strptime('Jan 1 2019', '%b %d %Y')
    endDate = datetime.strptime('Dec 31 2019', '%b %d %Y')

    lastYearSchedules = Schedule.objects.filter(workday__date__range=(startDate, endDate))

    for lastYearSchedule in lastYearSchedules:
        person = createPerson()[0]
        Appointment.objects.get_or_create(schedule=lastYearSchedule, person=person)
        Workdays.objects.filter(date=lastYearSchedule.workday.date).update(dosage=2400)

    startDate = datetime.strptime('Jan 1 2020', '%b %d %Y')
    endDate = datetime.today()

    workingDays = Workdays.objects.filter(date__range=(startDate, endDate)).all()

    for workingDay in workingDays:
        print(workingDay)
        workingDaySchedules = Schedule.objects.filter(workday=workingDay)
        sum_dosage = 0
        for workingDaySchedule in workingDaySchedules:
            person = createPerson()[0]
            Appointment.objects.get_or_create(schedule=workingDaySchedule, person=person)
            print(person)
            sum_dosage += dosage(person.bmi)

        Workdays.objects.filter(id=workingDay.id).update(dosage=sum_dosage)

    # currentYearSchedules = Schedule.objects.filter(workday__date__range=(startDate, endDate))


if __name__ == '__main__':
    # timeslot_seeder()
    # workdays_seeder()
    # schedule_seeder()
    appointments_seeder()
