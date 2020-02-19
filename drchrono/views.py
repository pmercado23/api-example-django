from django.shortcuts import redirect, HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import date
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from social_django.models import UserSocialAuth
from forms import CheckInForm, PatientUpdateProfileForm
from pprint import pprint


from drchrono.endpoints import DoctorEndpoint, PatientEndpoint, AppointmentEndpoint

# ToDo: Dr updates(DoctorWelcome), patient check-in views and temp, list of patients,


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_appointments_on_date(self, date):
        auth_token = self.get_token()
        appointments = AppointmentEndpoint(auth_token)
        return appointments.list(date=date)

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        appointment_list = list(self.get_appointments_on_date(date=date.today()))

        kwargs['doctor'] = doctor_details
        kwargs['appointments'] = appointment_list

        return kwargs


class PatientWelcome(TemplateView):
    """
    Patient facing for kiosk to check it
    """
    template_name = 'patient_welcome.html'

    def get_token(self):
        """
        ToDo: This is now used more than once, might move to its own file for commenly used code
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = __get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_context_data(self, **kwargs):
        kwargs = super(PatientWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        access_token = self.get_token()
        doctor_details = DoctorEndpoint(access_token)

        kwargs['doctor'] = next(doctor_details.list())

        return kwargs


class PatientCheckIn(FormView):
    template_name = 'patient_check_in.html'
    form_class = CheckInForm
    success_url = '/patient_update_profile/'
    patient_id = None

    def get_token(self):
        """
        ToDo: This is now used more than once, might move to its own file for commenly used code
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def form_valid(self, form):
        print('form valid ssn=', form.cleaned_data['ssn'])
        try:
            # gets token to call api
            token = self.get_token()
            patient_api_result = PatientEndpoint(token)
            patient_list = list(
                patient_api_result.list(
                    {
                        'first_name': str(form.cleaned_data['first_name']),
                        'last_name': str(form.cleaned_data['last_name']),
                        'social_security_number': form.cleaned_data['ssn']
                    }
                )
            )
            self.patient_id = patient_list[0]['id']
            print('patient_list = ', patient_list)

            return super(PatientCheckIn, self).form_valid(form)
        except Exception as e:
            print(e.message)
            return HttpResponseRedirect(reverse('patient_check_in'))

    def get_success_url(self):
        """ pass patient_id as a para to the success url """
        return reverse('patient_update_profile', kwargs={'patient_id': self.patient_id})

