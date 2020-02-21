from django.db import models
from django.utils import timezone

# Add your models here

class Appointment(models.Model):
    # Created a model to track in office Appointment data, patient_id, status and times of Appointment and arrival
    appointment_id = models.IntegerField()
    patient_id = models.IntegerField()
    status = models.CharField(max_length=50, blank=True, null=True)
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
