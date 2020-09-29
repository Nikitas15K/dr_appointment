from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Avg, Sum, Count
from celery.schedules import crontab
from celery.task import periodic_task
from .models import Appointment, Schedule, WaitingList, Workdays, Person, Sex
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

if datetime.today().strftime("%A") == 'Saturday':
    today_date = datetime.today() - timedelta(days=1)
    tomorrow_date = datetime.today() + timedelta(days=2)
elif datetime.today().strftime("%A") == 'Sunday':
    today_date = datetime.today() - timedelta(days=2)
    tomorrow_date = datetime.today() + timedelta(days=1)
else:
    today_date = datetime.today()
    tomorrow_date = datetime.today() + timedelta(days=1)


if datetime.today().strftime("%A") == 'Wednesday':
    second_day_date = tomorrow_date + timedelta(days=1)
    third_day_date = second_day_date + timedelta(days=3)
elif datetime.today().strftime("%A") == 'Thursday':
    second_day_date = tomorrow_date + timedelta(days=3)
    third_day_date = second_day_date + timedelta(days=4)
else:
    second_day_date = tomorrow_date + timedelta(days=1)
    third_day_date = second_day_date + timedelta(days=1)


def schedule(request, date):
    appointments = Appointment.objects.filter(schedule__workday__date=date) \
        .order_by('schedule__workday__date')
    people = Appointment.objects.filter(schedule__workday__date=date).values('person__bmi')
    today_dosage = get_sum_dosage(people)
    waiting_list = WaitingList.objects.all()

    all_schedules = Schedule.objects.filter(workday__date__range=(tomorrow_date, third_day_date))\
        .count()
    all_appointments = Appointment.objects\
        .filter(schedule__workday__date__range=(tomorrow_date, third_day_date)) \
        .all().count()
    context = {
        'appointments': appointments,
        'date': date,
        'now': datetime.now().time().hour,
        'current_dosage': today_dosage,
        'fixed_dosage': 2400,
        'fixed_difference': get_fixed_difference(today_dosage),
        'median_difference': get_median_difference(today_dosage),
        'avg_dosage': get_average_dosage(),
        'today': today_date,
        'tomorrow': tomorrow_date,
        'second_day': second_day_date,
        'third_day': third_day_date,
        'static_dosage': get_static_dosage(),
        'all_schedules': all_schedules,
        'all_appointments': all_appointments,
        'all_available': all_schedules - all_appointments,
        'waiting_list_count': waiting_list.count(),
    }

    return render(request, 'appointment/schedule.html', context)


def home(request):
    return schedule(request, today_date)


def tomorrow(request):
    return schedule(request, tomorrow_date)


def second_day(request):
    return schedule(request, second_day_date)


def third_day(request):
    return schedule(request, third_day_date)


def reporting(request):
    previous_year = str(today_date.year - 1)
    this_year = str(today_date.year)
    appointments = Appointment.objects.filter(schedule__workday__date__year=previous_year).all()
    df = pd.DataFrame(list(appointments.values('person__age'))).astype('float')
    df.hist()
    plt.suptitle('Age Distribution')
    plt.xlabel('age')
    plt.ylabel('patients')
    plt.savefig('appointment/static/appointment/age.png')

    df = pd.DataFrame(list(appointments.values('person__bmi'))).astype('float')
    df.hist()
    plt.suptitle('Bmi Distribution')
    plt.xlabel('bmi')
    plt.ylabel('patients')
    plt.savefig('appointment/static/appointment/bmi.png')

    df = pd.DataFrame(list(appointments.filter(person__sex=Sex.female).values('person__bmi'))).astype('float')
    df.hist()
    plt.suptitle('Female Bmi Distribution')
    plt.xlabel('bmi')
    plt.ylabel('patients')
    plt.savefig('appointment/static/appointment/female_bmi.png')

    df = pd.DataFrame(list(appointments.filter(person__sex=Sex.male).values('person__bmi'))).astype('float')
    df.hist()
    plt.suptitle('Male Bmi Distribution')
    plt.xlabel('bmi')
    plt.ylabel('patients')
    plt.savefig('appointment/static/appointment/male_bmi.png')

    df = pd.DataFrame(list(appointments.filter(person__smoker=True).values('person__bmi'))).astype('float')
    df.hist()
    plt.suptitle('Smoker bmi')
    plt.xlabel('bmi')
    plt.ylabel('patients')
    plt.savefig('appointment/static/appointment/smoker.png')

    df = pd.DataFrame(list(appointments.filter(person__smoker=False).values('person__bmi'))).astype('float')
    df.hist()
    plt.suptitle('No smoker bmi')
    plt.xlabel('bmi')
    plt.ylabel('count')
    plt.savefig('appointment/static/appointment/nosmoker.png')

    df = pd.DataFrame(Workdays.objects.filter(date__year=previous_year).all().order_by('date').values('date','dosage'))
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.plot()
    plt.xlabel('days of the year')
    plt.ylabel('daily dosage')
    plt.tight_layout()
    plt.savefig('appointment/static/appointment/dosage_previous_year.png')

    df = pd.DataFrame(Workdays.objects.filter(date__year=this_year).all().order_by('date').values('date', 'dosage'))
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.plot()
    plt.xlabel('days of the year')
    plt.ylabel('daily dosage')
    plt.tight_layout()
    plt.savefig('appointment/static/appointment/dosage_current_year.png')

    dosage_sum_current_year_column = df.iloc[:, 0]
    dosage_sum_current_year = dosage_sum_current_year_column.sum()
    average_dosage_per_day = round((dosage_sum_current_year / df.count()), 2)
    average_dosage_per_day = average_dosage_per_day[0]
    appointment_count_current_year = (Appointment.objects.filter(schedule__workday__date__year=this_year).all()).count()

    # df = pd.DataFrame.from_dict((appointments.values('person__sex').aggregate(Count('person__sex'))))
    # df.plot(kind='bar')
    # plt.savefig('appointment/static/appointment/sex.png')

    all_schedules = Schedule.objects.filter(workday__date__range=(tomorrow_date, third_day_date)) \
        .count()
    all_appointments = Appointment.objects \
        .filter(schedule__workday__date__gte=tomorrow_date, schedule__workday__date__lte=third_day_date) \
        .all().count()
    waiting_list = WaitingList.objects.order_by('created_at').all()


    context = {
        'previous_year': previous_year,
        'appointment_number': appointments.count(),
        'avg_bmi': round(appointments.values('person__bmi').aggregate(Avg('person__bmi'))['person__bmi__avg'], 2),
        'date': today_date,
        'now': datetime.now().time().hour,
        'today': today_date,
        'tomorrow': tomorrow_date,
        'second_day': second_day_date,
        'third_day': third_day_date,
        'all_schedules': all_schedules,
        'all_appointments': all_appointments,
        'all_available': all_schedules - all_appointments,
        'waiting_list_count': waiting_list.count(),
        'this_year': this_year,
        'average_dosage_per_day':average_dosage_per_day,
        'appointment_count_current_year':appointment_count_current_year,
    }

    return render(request, 'appointment/report.html', context)


def get_average_dosage():
    endDate = datetime.strptime('Dec 31 2019', '%b %d %Y')
    avg_dosage = Workdays.objects.filter(date__gt=endDate). \
        exclude(dosage__isnull=True). \
        annotate(Avg('dosage')).values('dosage__avg').first()['dosage__avg']

    return round(avg_dosage, 2)


def get_median_difference(dosage):
    return dosage - get_average_dosage()


def get_fixed_difference(dosage):
    return dosage - 2400


def get_sum_dosage(bmis):
    sum = 0
    for bmi in bmis:
        sum += dosage(bmi['person__bmi'])

    return sum


def dosage(bmi):
    bmi = float(bmi)
    formula = (0.0091 * bmi ** 3) - (0.7925 * bmi ** 2) + (25.89 * bmi) - 79.442

    return round(float(formula), 2)


def get_static_dosage():
    return 2400


# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week="mon"))
def make_day_planning(request):
    workdays = Workdays.objects.filter(date__range=(tomorrow_date, third_day_date))
    waiting_list = WaitingList.objects.order_by('created_at').all()

    # TODO This will change to Smart Selection
    if waiting_list.count() > 0:
        available_schedules = get_availables_schedules()
        print(available_schedules)
        if available_schedules.count() > 0:
            for available_schedule in available_schedules:
                if waiting_list.count() > 0:
                    person_in_waiting_list = waiting_list[0].person
                    Appointment.objects.create(schedule=available_schedule, person=person_in_waiting_list)
                    waiting_list[0].delete()

            # Update workday sum dosage
            for workday in workdays:
                workday_appointments = Appointment.objects.filter(schedule__workday=workday)
                sum_dosage = 0
                for workday_appointment in workday_appointments:
                    sum_dosage += dosage(workday_appointment.person.bmi)

                Workdays.objects.filter(pk=workday.id).update(dosage=sum_dosage)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_availables_schedules():
    all_schedules = Schedule.objects.filter(workday__date__gte=tomorrow_date, workday__date__lte=third_day_date).all()
    scheduled_appointments = Appointment.objects\
        .filter(schedule__workday__date__range=(tomorrow_date, third_day_date))\
        .values_list('id', flat=True)
    available_schedules = all_schedules.exclude(appointment__in=scheduled_appointments).order_by('workday')

    return available_schedules


def delete_from_waiting_list(request, id):
    appointment = Appointment.objects.filter(id=id).first()
    person = appointment.person
    substitute_appointment(appointment)
    WaitingList.objects.create(person=person)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def readd_to_waiting_list(request, id):
    appointment = Appointment.objects.filter(id=id).first()
    person = appointment.person
    appointment.delete()
    WaitingList.objects.create(person=person)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def substitute_appointment(appointment):
    workday = appointment.schedule.workday
    this_day_appointments = Appointment.objects.values('person__bmi').filter(schedule__workday=workday)

    selected_person = WaitingList.objects.order_by('person__bmi').exclude(person=appointment.person).first()
    if selected_person:
        WaitingList.objects.order_by('person__bmi').get(person__amka=selected_person).delete()
        new_appointment = Appointment.objects.get(id=appointment.id)
        new_appointment.person = Person.objects.get(amka=selected_person)
        new_appointment.save()


def accomplished(request, id):
    appointment = Appointment.objects.filter(id=id).first()
    appointment.accomplished = True
    appointment.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def canceled(request, id):
    appointment = Appointment.objects.filter(id=id).first()
    appointment.accomplished = False
    appointment.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_day_availables(day):
    day_schedules = Schedule.objects.filter(workday__date=day).all()
    day_appointments = Appointment.objects.filter(schedule__workday__date=day).values_list('id', flat=True)
    return day_schedules.exclude(appointment__in=day_appointments)


def manual_appointment(request):
    schedule_id = request.POST.getlist('schedule')[0]
    person_amka = request.POST.getlist('person')[0]

    Appointment.objects.create(person=Person.objects.get(amka=int(person_amka)), schedule=Schedule.objects.get(id=int(schedule_id)))
    WaitingList.objects.get(person=Person.objects.get(amka=int(person_amka))).delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def manual_schedule(request):
    waiting_list = WaitingList.objects.order_by('created_at').all()
    tomorrow_availables = get_day_availables(tomorrow_date)
    second_day_availables = get_day_availables(second_day_date)
    third_day_availables = get_day_availables(third_day_date)
    all_schedules = Schedule.objects.filter(workday__date__range=(tomorrow_date, third_day_date)) \
        .count()
    all_appointments = Appointment.objects \
        .filter(schedule__workday__date__gte=tomorrow_date, schedule__workday__date__lte=third_day_date) \
        .all().count()

    context = {
        'date': today_date,
        'now': datetime.now().time().hour,
        'today': today_date,
        'tomorrow': tomorrow_date,
        'second_day': second_day_date,
        'third_day': third_day_date,
        'waiting_list': waiting_list,
        'tomorrow_availables': tomorrow_availables,
        'second_day_availables': second_day_availables,
        'third_day_availables': third_day_availables,
        'all_schedules': all_schedules,
        'all_appointments': all_appointments,
        'all_available': all_schedules - all_appointments,
        'waiting_list_count': waiting_list.count(),
    }
    return render(request, 'appointment/manual.html', context)