from django.shortcuts import redirect, HttpResponseRedirect, render
from django.core.urlresolvers import reverse
from datetime import date
from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from social_django.models import UserSocialAuth
from forms import CheckInForm, PatientDemographicForm

from utils import get_token
from models import Appointment
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

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_appointments_on_date(self, date):
        auth_token = get_token()
        appointments = AppointmentEndpoint(auth_token)
        return appointments.list(date=date)

    def get_patients(self):
        auth_token = get_token()
        patients = PatientEndpoint(auth_token)
        return patients.list()

    def get_check_in_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = Appointment.objects.all().filter(
            status='Arrived')
        for appointment in checked_in_appointments:
            appointment.wait_since_arrived = appointment.get_time_waiting()
            patient = [patient for patient in patient_list if patient.get('id') == appointment.patient_id][0]
            appointment.first_name = patient.get('first_name')
            appointment.last_name = patient.get('last_name')

        return checked_in_appointments

    def update_appointment_data(self, appointment_list):
        # here on loading, if there is already data with missing times in it, we populate it here.
        for patient in appointment_list:
            appointment, created = Appointment.objects.get_or_create(
                appointment_id=patient.get('id'),
                patient_id=patient.get('patient'),
                status=patient.get('status'),
                scheduled_time=patient.get('scheduled_time')
            )

            if appointment.status == 'Arrived' and not appointment.arrival_time:
                appointment.arrival_time = timezone.now()

            appointment.save()

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        patient_list = list(self.get_patients())
        appointment_list = list(self.get_appointments_on_date(date=date.today()))

        for appointment in appointment_list:
            patient = [patient for patient in patient_list if patient.get('id') == appointment.get('patient')][0]
            print(patient.get('first_name'))
            print(patient.get('date_of_birth'))
            print(patient.get('social_security_number'))
            appointment['first_name'] = patient.get('first_name')
            appointment['last_name'] = patient.get('last_name')
        self.update_appointment_data(appointment_list)

        kwargs['doctor'] = doctor_details
        kwargs['appointments'] = appointment_list
        kwargs['checked_in'] = self.get_check_in_patients(patient_list=patient_list)

        return kwargs


class PatientWelcome(View):
    """
    Patient facing for kiosk to check in
    """

    def get(self, request, *args, **kwargs):
        # GET send a blank form for the patient
        template = 'patient_welcome.html'
        doctor = next(DoctorEndpoint(get_token()).list())

        return render(request, template, {'doctor': doctor})


class PatientCheckIn(View):
    # Here we have 2 methods, GET and POST, GET will display the form, and POST will check and store the data
    def get(self, request, *args, **kwargs):
        # GET send a blank form for the pacent
        template = 'patient_check_in.html'
        form = CheckInForm()

        return render(request, template, {'form': form})

    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = CheckInForm(request.POST)
        # we need to get the list of pacents on the appointment to check if they are checking in or if its a walkin

        if form.is_valid():
            first_name, last_name, dob, ssn = form.cleaned_data.get('first_name'), \
                                              form.cleaned_data.get('last_name'), \
                                              form.cleaned_data.get('dob'), \
                                              form.cleaned_data.get('ssn')
            dob_list = dob.split('/')[::-1]
            date_of_birth = dob_list[0] + "-" + dob_list[2] + "-" + dob_list[1]

            access_token = get_token()
            appointment_api = AppointmentEndpoint(access_token)
            patient_api = PatientEndpoint(access_token)

            patients = list(patient_api.list())
            patient = None

            for i in patients:
                if (i.get('first_name') == first_name and
                        i.get('last_name') == last_name and
                        i.get('date_of_birth') == date_of_birth and
                        i.get('social_security_number') == ssn):
                    patient = i
                print(i)

            if not patient:
                pprint("no patient found")
                return HttpResponseRedirect('/patient_welcome/')
                # handle not finding someone

            # here we assume we found the patent, now we check if they have any appointments today

            today = timezone.now()
            today_str = today.strftime('%m-%d-%y')
            appointments = list(
                appointment_api.list({'patient': patient.get('id')}, start=today_str,
                                     end=today_str))

            if len(appointments) < 1:
                print("no appointment today?")
                # handle no appointment for today found
            # Handle multiple appointments?
            appointment_api.update(appointments[0].get('id'), {'status': 'Arrived'})

            # locally set status to Arrived, and arrival_time to right now
            appointment, created = Appointment.objects.get_or_create(
                appointment_id=appointments[0].get('id'),
                patient_id=patient.get('id'))

            if not created and appointment.status == 'Arrived':
                # Here we return that they have already checked in
                print("already here! cancel or change?")
                return redirect('patient_demographic_information', patient_id=patient.get('id'))

            appointment.arrival_time = timezone.now()
            appointment.status = 'Arrived'
            appointment.save()
            # redirect to demographic information page
            return redirect('patient_demographic_information', patient_id=patient.get('id'))

        return render(request, 'patient_check_in.html', {'form': form})


class PatientDemographicInformation(View):
    # Here we have 2 methods, GET and POST, GET will display the form, and POST will check and store the data
    # First we get and display demographic information and offer to update

    def get(self, request, patient_id):
        template = 'patient_demographics.html'
        access_token = get_token()
        patient_api = PatientEndpoint(access_token)
        patient_data = patient_api.fetch(patient_id)
        form = PatientDemographicForm(initial=patient_data)
        return render(request, template,
                      {'form': form, 'patient_id': patient_id})

    def post(self, request, patient_id):
        template = 'patient_demographics.html'

        # create a form instance and populate it with data from the request:
        form = PatientDemographicForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            access_token = get_token()
            patient_api = PatientEndpoint(access_token)
            patient_api.update(patient_id, form.cleaned_data)

            return HttpResponseRedirect('/finished/')

        return render(request, template,
                      {'form': form, 'patient_id': patient_id})

class FinishedView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'checkin_finished.html'
