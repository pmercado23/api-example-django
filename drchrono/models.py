from django.db import models
from django.utils import timezone

# Add your models here

class Appointment(models.Model):
    # Created a model to track in office Appointment data, patient_id, status and times of Appointment and arrival
    appointment_id = models.IntegerField()
    patient_id = models.IntegerField()
    status = models.CharField(max_length=50, blank=True, null=True)
    reason = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    arrival_time = models.DateTimeField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def get_time_waiting(self):
        if not self.arrival_time:
            return "Has Not Checked In"
        if self.start_time:
            return self.start_time - self.arrival_time
        return timezone.now() - self.arrival_time

    def get_appointment_duration(self):
        if not self.start_time:
            return "Visit hasn't started"
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time


class Patient(models.Model):
    # Created a model to track in Patient data, patient_id
    patient_id = models.IntegerField()
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    middle_name = models.CharField(max_length=200, blank=True, null=True)
    nick_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    ethnicity = models.CharField(max_length=200, blank=True, null=True)
    date_of_birth = models.CharField(max_length=50, blank=True, null=True)
    default_pharmacy = models.CharField(max_length=200, blank=True, null=True)
    cell_phone = models.CharField(max_length=20, blank=True, null=True)
    patient_photo = models.CharField(max_length=400, blank=True, null=True)
    preferred_language = models.CharField(max_length=200, blank=True, null=True)
    race = models.CharField(max_length=50, blank=True, null=True)
    social_security_number = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
