from django.shortcuts import HttpResponseRedirect
from datetime import datetime
from django.views.generic import TemplateView
from django.utils import timezone
from django.views import View
from drchrono.utils import get_token, combine_patient_to_appointment
from drchrono.models import Appointment, Patient

from drchrono.endpoints import DoctorEndpoint, PatientEndpoint, AppointmentEndpoint


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
        return combine_patient_to_appointment(patient_list, appointments)

    def get_check_in_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='Arrived')
        return combine_patient_to_appointment(patient_list, checked_in_appointments)

    def get_in_session_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='In Session')
        return combine_patient_to_appointment(patient_list, checked_in_appointments)

    def get_seen_patients(self, patient_list):
        # getting the list of patents who have check in.
        checked_in_appointments = self.get_todays_appointment_by_status(status='Complete')
        return combine_patient_to_appointment(patient_list, checked_in_appointments)


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