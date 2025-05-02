from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('contact-us', views.contact, name='contact'),
    path('about', views.about, name='about'),
    path('booking', views.booking, name='booking'),
    path('booking-submit', views.bookingSubmit, name='bookingSubmit'),
    path('user-panel', views.userPanel, name='userPanel'),
    path('user-update/<int:id>', views.userUpdate, name='userUpdate'),
    path('user-update-submit/<int:id>', views.userUpdateSubmit, name='userUpdateSubmit'),
    path('staff-panel', views.staffPanel, name='staffPanel'),
    path('delete_appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('edit_appointment/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('cancel-appointment/<int:appointment_id>/', views.cancelAppointment, name='cancelAppointment'),
]

# ADD THIS
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
