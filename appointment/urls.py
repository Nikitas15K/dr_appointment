from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='appointment-home'),
    path('tomorrow', views.tomorrow, name='appointment-tomorrow'),
    path('second-day', views.second_day, name='appointment-second'),
    path('third-day', views.third_day, name='appointment-third'),
    path('reporting', views.reporting, name='appointment-reporting'),
    path('plan', views.make_day_planning, name='appointment-planning'),
    path('delete/<int:id>', views.delete_from_waiting_list),
    path('readd/<int:id>', views.readd_to_waiting_list),
    path('accomplished/<int:id>', views.accomplished),
    path('canceled/<int:id>', views.canceled),
    path('manual/', views.manual_schedule, name='manual'),
    path('schedule/', views.manual_appointment, name='schedule'),
]

