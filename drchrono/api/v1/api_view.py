from django.contrib.auth.models import User, Group
from drchrono.models import Appointment, Patient
from rest_framework import viewsets
from serializers import UserSerializer, GroupSerializer, AppointmentSerializer, PatientSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Appointments to be viewed or edited.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Appointments to be viewed or edited.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
