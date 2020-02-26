from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
from rest_framework import routers
from api.v1 import api_view

admin.autodiscover()

import views

router = routers.DefaultRouter()
router.register(r'users', api_view.UserViewSet)
router.register(r'groups', api_view.GroupViewSet)
router.register(r'appointment', api_view.AppointmentViewSet)
router.register(r'patient', api_view.PatientViewSet)


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^sync/$', views.DataSync.as_view(), name='data_sync'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^patient_welcome/$', views.PatientWelcome.as_view(), name='patient_welcome'),
    url(r'^patient_new/$', views.PatientNew.as_view(), name='patient_new'),
    url(r'^patient_check_in/', views.PatientCheckIn.as_view(), name='patient_check_in'),
    url(r'^patient_demographics/(?P<patient_id>\d+)/$', views.PatientDemographicInformation.as_view(),
        name='patient_demographic_information'),
    url(r'^finished/$', views.FinishedView.as_view(), name='finished'),
    url(r'^toggle-timer/(?P<appointment_id>\d+)/$', views.UpdateAppointmentStatusView.as_view(), name='update_appointment_status'),
    url(r'^patient_details/(?P<patient_id>\d+)/$', views.PatientDetails.as_view(), name='patient_details'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls)),
]