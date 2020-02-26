from django.shortcuts import redirect, HttpResponseRedirect, render
from django.core.urlresolvers import reverse
from datetime import date, datetime
from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from social_django.models import UserSocialAuth
from django.forms.models import model_to_dict
from forms import CheckInForm, PatientDemographicForm

from utils import get_token, combine_patient_to_appointment, check_ssn_format, new_combine_patient_to_appointment
from models import Appointment, Patient
from pprint import pprint

from drchrono.endpoints import DoctorEndpoint, PatientEndpoint, AppointmentEndpoint


# ToDo: Dr updates(DoctorWelcome), patient check-in views and temp, list of patients,


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DataSync(View):
    """
    adding data sync endpoint to avoid calling api's on every load
    """

    def get_appointments_on_date(self, date):
        auth_token = get_token()
        appointments = AppointmentEndpoint(auth_token)
        return list(appointments.list(date=date))

    def get_patients(self):
        auth_token = get_token()
        patients = PatientEndpoint(auth_token)
        return list(patients.list())

    def update_appointment_data(self, patient_list, appointment_list):
        # here on loading, if there is already data with missing times in it, we populate it here.
        for appointment in appointment_list:
            patient = [patient for patient in patient_list if patient.patient_id == appointment.get('patient')][0]

            appointment_obj, created = Appointment.objects.get_or_create(
                appointment_id=appointment.get('id'),
                patient_id=patient.patient_id,
                status=appointment.get('status'),
                scheduled_time=appointment.get('scheduled_time'),
                reason=appointment.get('reason'),
                notes = appointment.get('notes')
            )

            if appointment_obj.status == 'Arrived' and not appointment_obj.arrival_time:
                appointment_obj.arrival_time = timezone.now()

            appointment_obj.save()

    def update_patient_data(self, patient_list):
        # here on loading, if there is already data with missing times in it, we populate it here.
        for patient in patient_list:
            Patient.objects.get_or_create(
                patient_id= patient.get('id'),
                first_name = patient.get('first_name'),
                last_name = patient.get('last_name'),
                middle_name = patient.get('middle_name'),
                nick_name = patient.get('nick_name'),
                email=patient.get('email'),
                gender = patient.get('gender'),
                ethnicity = patient.get('ethnicity'),
                date_of_birth = patient.get('date_of_birth'),
                default_pharmacy = patient.get('default_pharmacy'),
                cell_phone = patient.get('cell_phone'),
                patient_photo = patient.get('patient_photo'),
                preferred_language = patient.get('preferred_language'),
                race = patient.get('race'),
                social_security_number = patient.get('social_security_number'),
                emergency_contact_name = patient.get('emergency_contact_name'),
                emergency_contact_phone = patient.get('emergency_contact_phone'),
                emergency_contact_relation = patient.get('emergency_contact_relation')
            )

        return Patient.objects.all()


    def get(self, request, *args, **kwargs):
        # First get lists from api
        patient_list = self.get_patients()
        appointment_list = self.get_appointments_on_date(date=date.today())
        # then create objects
        patients = self.update_patient_data(patient_list)
        self.update_appointment_data(patients, appointment_list)

        return redirect('welcome')


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

    def get_all_patients(self):
        return Patient.objects.all()

    def get_todays_appointment_by_status(self, status):
        today = timezone.now()
        return Appointment.objects.all().filter(
            status=status,
            scheduled_time__year=today.year,
            scheduled_time__month=today.month,
            scheduled_time__day=today.day)

    def get_todays_appointments(self, patient_list):
        today = timezone.now()
        appointments = Appointment.objects.all().filter(
            scheduled_time__year=today.year,
            scheduled_time__month=today.month,
            scheduled_time__day=today.day)
        return new_combine_patient_to_appointment(patient_list, appointments)

    def get_check_in_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='Arrived')
        return new_combine_patient_to_appointment(patient_list, checked_in_appointments)

    def get_in_session_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='In Session')
        return new_combine_patient_to_appointment(patient_list, checked_in_appointments)

    def get_seen_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='Complete')
        return new_combine_patient_to_appointment(patient_list, checked_in_appointments)


    def avg_wait_time(self):
        appointments = self.get_todays_appointment_by_status(status='Arrived')
        if len(appointments) <= 0:
            return datetime.fromtimestamp(0).strftime("%H:%M:%S")
        total_seconds = sum([(appointment.get_time_waiting()).seconds for appointment in appointments]) / len(
            appointments)
        return datetime.fromtimestamp(total_seconds).strftime("%H:%M:%S")

    def avg_appointment_time(self):
        appointments = self.get_todays_appointment_by_status(status='Complete')
        if len(appointments) <= 0:
            return datetime.fromtimestamp(0).strftime("%H:%M:%S")
        total_seconds = sum([(appointment.end_time - appointment.start_time).seconds for appointment in appointments]) / len(
            appointments)
        return datetime.fromtimestamp(total_seconds).strftime("%H:%M:%S")

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        patient_list = Patient.objects.all()

        kwargs['doctor'] = doctor_details
        kwargs['appointments'] = self.get_todays_appointments(patient_list=patient_list)
        kwargs['checked_in'] = self.get_check_in_patients(patient_list=patient_list)
        kwargs['in_session'] = self.get_in_session_patients(patient_list=patient_list)
        kwargs['seen'] = self.get_seen_patients(patient_list=patient_list)
        kwargs['avg_wait_time'] = self.avg_wait_time()
        kwargs['avg_appointment_time'] = self.avg_appointment_time()

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


class PatientNew(View):
    """
    Response if no patient found
    """
    def get(self, request, *args, **kwargs):
        # GET send a blank form for the patient
        template = 'patient_new.html'
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
        # we need to get the list of pacents on the appointment to check if they are checking in or if its a walk-in
        data = request.POST.copy()
        ssn = data.get('ssn')
        access_token = get_token()
        appointment_api = AppointmentEndpoint(access_token)

        if form.is_valid() and check_ssn_format(ssn):
            first_name, last_name, date_of_birth = form.cleaned_data.get('first_name'), \
                                                   form.cleaned_data.get('last_name'), \
                                                   form.cleaned_data.get('date').strftime('%Y-%m-%d')

            # here we get data from App and Pa django objects instead
            p = Patient.objects.get(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                social_security_number=ssn
            )
            try:
                p = Patient.objects.get(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    social_security_number=ssn
                )
            except Patient.DoesNotExist:
                p = None

            if not p:
                return HttpResponseRedirect('/patient_new/')

            wi = form.cleaned_data.get('walk_in')

            if wi:
                doctor = next(DoctorEndpoint(get_token()).list())
                create_appointment = {
                    'status': 'Arrived',
                    'duration': 30,
                    'date': timezone.now(),
                    'doctor': doctor.get('id'),
                    'patient': p.patient_id,
                    'scheduled_time': timezone.now(),
                    'exam_room': 0,
                    'office': 276816,  # hardcoded for now
                    'notes': 'Walk-In'

                }
                created_appointment = appointment_api.create(create_appointment)

                appointment, created = Appointment.objects.get_or_create(
                    appointment_id=created_appointment.get('id'),
                    patient_id=p.patient_id,
                    scheduled_time=created_appointment.get('scheduled_time'),
                    notes=created_appointment.get('notes')
                )
            else:
                today = timezone.now()
                try:
                    appointment = Appointment.objects.get(
                        patient_id=p.patient_id,
                        scheduled_time__year=today.year,
                        scheduled_time__month=today.month,
                        scheduled_time__day=today.day
                    )
                except Appointment.DoesNotExist:
                    form.add_error('first_name', "We are sorry, but we could not find you on todays list, is this a walk-in?")
                    return render(request, 'patient_check_in.html', {'form': form})

                appointment_api.update(appointment.appointment_id, {'status': 'Arrived'})

            if (appointment.status == 'Arrived'):
                # Here we return that they have already checked in
                return redirect('patient_demographic_information', patient_id=p.patient_id)

            appointment.arrival_time = timezone.now()
            appointment.status = 'Arrived'
            appointment.save()
            # redirect to demographic information page
            return redirect('patient_demographic_information', patient_id=p.patient_id)

        form.add_error('ssn', "Please Enter a Valid SSN in format 123-44-1234")

        return render(request, 'patient_check_in.html', {'form': form})


class PatientDemographicInformation(View):
    # Here we have 2 methods, GET and POST, GET will display the form, and POST will check and store the data
    # First we get and display demographic information and offer to update
    def get(self, request, patient_id):
        template = 'patient_demographics.html'
        patient = Patient.objects.get(patient_id=patient_id)
        form = PatientDemographicForm(initial=model_to_dict(patient))
        return render(request, template,
                      {'form': form, 'patient_id': patient_id})

    def post(self, request, patient_id):
        template = 'patient_demographics.html'
        # create a form instance and populate it with data from the request:
        patient = Patient.objects.get(patient_id=patient_id)
        # check whether it's valid:
        form = PatientDemographicForm(request.POST or None, instance=patient)
        if form.is_valid():
            access_token = get_token()
            patient_api = PatientEndpoint(access_token)
            patient_api.update(patient_id, form.cleaned_data)
            patient.save()

            return HttpResponseRedirect('/finished/')

        return render(request, template,
                      {'form': form, 'patient_id': patient_id})


class FinishedView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'checkin_finished.html'


class UpdateAppointmentStatusView(View):
    def change_status(self, status, appointment):
        access_token = get_token()
        appointment_api = AppointmentEndpoint(access_token)
        if status == "Arrived":
            appointment_api.update(appointment.appointment_id, {'status': 'In Session'})
            appointment.start_time = timezone.now()
            appointment.status = "In Session"
            appointment.save()
        elif status == "In Session":
            appointment_api.update(appointment.appointment_id, {'status': 'Complete'})
            appointment.end_time = timezone.now()
            appointment.status = "Complete"
            appointment.save()
        else:
            print("Something went wrong here")

    def update_status(self, appointment_id):
        appointments = Appointment.objects.filter(appointment_id=appointment_id)
        for appointment in appointments:
            self.change_status(appointment.status, appointment)

    def post(self, request, appointment_id):
        self.update_status(appointment_id)
        return HttpResponseRedirect('/welcome/')


class PatientDetails(View):
    """
    Response if no patient found
    """
    def get(self, request, patient_id):
        # GET send a blank form for the patient
        template = 'patient_details.html'
        access_token = get_token()
        patient_api = PatientEndpoint(access_token)
        patient = patient_api.fetch(patient_id)

        return render(request, template, {'patient': patient})
