from django.db import models
from enum import Enum
from django_enum_choices.fields import EnumChoiceField
from datetime import datetime, timedelta


class Sex(Enum):
    male = "MALE"
    female = "FEMALE"


class Person(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    amka = models.CharField(max_length=10, primary_key=True)
    smoker = models.BooleanField(default=0)
    children = models.IntegerField(default=0)
    age = models.IntegerField(default=0, blank=False)
    sex = EnumChoiceField(Sex, blank=False)
    height = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    weight = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    bmi = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    phone = models.CharField(max_length=10, blank=False)
    address = models.CharField(max_length=100, blank=False)

    def save(self, *args, **kwargs):
        self.bmi = self.weight / self.height ** 2 * 10 ** 4
        super(Person, self).save(*args, **kwargs)

    def __str__(self):
        return self.amka + ": " + self.first_name + " " + self.last_name


class WaitingList(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return str(self.person.amka)

    def save(self, *args, **kwargs):
        if self.waiting_list_has_available():
            if not self.already_in_list():
                super().save(*args, **kwargs)

    def already_in_list(self):
        if WaitingList.objects.filter(person=self.person).count() > 0:
            return True
        else:
            return False

    def waiting_list_has_available(self):
        waiting_list_size = WaitingList.objects.count()
        person_already_in_appointments = Appointment.objects.filter(schedule__workday__date__gt=datetime.today())\
            .filter(person__amka=self.person.amka).count()

        two_week_schedules = Schedule.objects.filter(workday__date__range=(datetime.today(), datetime.today() + timedelta(days=14)))
        two_week_appointments = Appointment.objects.filter(schedule__workday__date__range=(datetime.today(), datetime.today() + timedelta(days=14)))\
            .values_list('id', flat=True)
        two_week_availables = two_week_schedules.exclude(appointment__in=two_week_appointments).count()

        if waiting_list_size < two_week_availables:
            if person_already_in_appointments:
                return False
            else:
                return True


class Workdays(models.Model):
    date = models.DateField('date')
    dosage = models.FloatField(default=None, blank=True, null=True)

    # def __str__(self):
    #     return str(self.date)


class TimeSlot(models.Model):
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)


class Schedule(models.Model):
    workday = models.ForeignKey(Workdays, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.workday.date) + ', Time: ' + str(self.timeslot.start_time) + ':00 - ' + str(
            self.timeslot.end_time) + ':00'


class Appointment(models.Model):
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, unique=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    accomplished = models.BooleanField(default=0, null=True)

    class Meta:
        ordering = ['-schedule']



