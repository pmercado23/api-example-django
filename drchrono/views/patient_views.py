from django.shortcuts import redirect, HttpResponseRedirect, render
from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from django.forms.models import model_to_dict
from drchrono.forms import CheckInForm, PatientDemographicForm

from drchrono.utils import get_token, check_ssn_format
from drchrono.models import Appointment, Patient

from drchrono.endpoints import DoctorEndpoint, PatientEndpoint, AppointmentEndpoint



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
