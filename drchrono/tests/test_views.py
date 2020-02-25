
import time

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint
from drchrono.models import Appointment
from drchrono.views import *
from drchrono import utils


class SetupViewTests(TestCase):
    # Testing setup view
    def test_kiosk_setup(self):
        response = self.client.get(reverse('setup'))
        self.assertEqual(response.status_code, 200)


class CheckInViewTests(TestCase):
    # testing check-in view
    def setUp(self):
        self.view = PatientCheckIn()

    def test_get(self):
        # should always return a 200
        response = self.client.get(reverse('patient_check_in'))
        self.assertEqual(200, response.status_code)


class FinishedViewTests(TestCase):
    def setUp(self):
        self.view = FinishedView()
    # Testing setup view
    def test_kiosk_setup(self):
        response = self.client.get(reverse('finished'))
        self.assertEqual(response.status_code, 200)
