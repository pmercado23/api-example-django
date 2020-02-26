from django.shortcuts import redirect
from datetime import date
from django.views import View
from django.utils import timezone
from drchrono.utils import get_token
from drchrono.models import Appointment, Patient

from drchrono.endpoints import PatientEndpoint, AppointmentEndpoint


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
