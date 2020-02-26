from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from api.v1 import api_view
from views import data_sync_views, doctor_views, setup_views, patient_views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', api_view.UserViewSet)
router.register(r'groups', api_view.GroupViewSet)
router.register(r'appointment', api_view.AppointmentViewSet)
router.register(r'patient', api_view.PatientViewSet)


urlpatterns = [
    url(r'^setup/$', setup_views.SetupView.as_view(), name='setup'),
    url(r'^sync/$', data_sync_views.DataSync.as_view(), name='data_sync'),
    url(r'^welcome/$', doctor_views.DoctorWelcome.as_view(), name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^patient_welcome/$', patient_views.PatientWelcome.as_view(), name='patient_welcome'),
    url(r'^patient_new/$', patient_views.PatientNew.as_view(), name='patient_new'),
    url(r'^patient_check_in/', patient_views.PatientCheckIn.as_view(), name='patient_check_in'),
    url(r'^patient_demographics/(?P<patient_id>\d+)/$', patient_views.PatientDemographicInformation.as_view(),
        name='patient_demographic_information'),
    url(r'^finished/$', patient_views.FinishedView.as_view(), name='finished'),
    url(r'^toggle-timer/(?P<appointment_id>\d+)/$', doctor_views.UpdateAppointmentStatusView.as_view(), name='update_appointment_status'),
    url(r'^patient_details/(?P<patient_id>\d+)/$', patient_views.PatientDetails.as_view(), name='patient_details'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls)),
]