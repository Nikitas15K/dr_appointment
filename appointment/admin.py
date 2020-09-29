from django.contrib import admin
from .models import Person, Appointment, Schedule, WaitingList
from datetime import datetime, timedelta
from django.contrib import messages


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('person', 'schedule')
    fields = ('schedule', 'person')
    list_per_page = 25

    my_schedule_for_formfield = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Appointment, AppointmentAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'amka', 'age', 'sex', 'bmi')
    search_fields = ['amka']
    fields = ('first_name', 'last_name', 'amka', 'age',
              'sex', 'children', 'height', 'weight', 'phone', 'address')
    list_per_page = 25


admin.site.register(Person, PersonAdmin)


class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('person', 'created_at')
    fields = ('person', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('person__amka', 'person__first_name', 'person__last_name',)
    list_per_page = 100
    autocomplete_fields = ['person']

    def save_model(self, request, obj, form, change):
        if self.already_in_list(obj):
            messages.set_level(request, messages.ERROR)
            messages.error(request, "Already in waiting list!")
        else:
            if self.already_in_appointments(obj):
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Person already has an appointment!")
            else:
                if self.waiting_list_has_available():
                    super(WaitingListAdmin, self).save_model(request, obj, form, change)
                else:
                    messages.set_level(request, messages.ERROR)
                    messages.error(request, "Waiting list is full!")


    def already_in_appointments(self, obj):
        if Appointment.objects.filter(person__amka=obj)\
                .filter(schedule__workday__date__gt=datetime.today()).count() > 0:
            return True
        else:
            return False

    def already_in_list(self, obj):
        if WaitingList.objects.filter(person__amka=obj).count() > 0:
            return True
        else:
            return False

    def waiting_list_has_available(self):
        waiting_list_size = WaitingList.objects.count()
        two_week_schedules = Schedule.objects.filter(
            workday__date__range=(datetime.today(), datetime.today() + timedelta(days=14)))
        two_week_appointments = Appointment.objects.filter(
            schedule__workday__date__range=(datetime.today(), datetime.today() + timedelta(days=14))) \
            .values_list('id', flat=True)
        two_week_availables = two_week_schedules.exclude(appointment__in=two_week_appointments).count()

        if waiting_list_size < two_week_availables:
            return True
        else:
            return False

    def has_add_permission(self, request):
        if self.waiting_list_has_available():
            return True

        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(WaitingList, WaitingListAdmin)
admin.site.site_header = 'BioScan Clinic AdminPanel'
