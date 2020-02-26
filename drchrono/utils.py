from social_django.models import UserSocialAuth
import re


def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.

    Moved this into its own location to better use in multiple places
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token


def combine_patient_to_appointment(patient_list, appointment_list):
    for appointment in appointment_list:
        patient = [patient for patient in patient_list if patient.patient_id == appointment.patient_id][0]
        appointment.wait_since_arrived = appointment.get_time_waiting()
        appointment.appointment_duration = appointment.get_appointment_duration()
        appointment.first_name = patient.first_name
        appointment.last_name = patient.last_name
    return appointment_list


def check_ssn_format(form_dob):
    r = re.compile('.{3}-.{2}-.{4}')
    return bool(r.match(form_dob))
