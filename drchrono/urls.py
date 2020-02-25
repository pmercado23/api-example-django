from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^patient_welcome/$', views.PatientWelcome.as_view(), name='patient_welcome'),
    url(r'^patient_new/$', views.PatientNew.as_view(), name='patient_new'),
    url(r'^patient_check_in/', views.PatientCheckIn.as_view(), name='patient_check_in'),
    url(r'^patient_demographics/(?P<patient_id>\d+)/$', views.PatientDemographicInformation.as_view(),
        name='patient_demographic_information'),
    url(r'^finished/$', views.FinishedView.as_view(), name='finished'),

]