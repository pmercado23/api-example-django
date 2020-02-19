from django import forms
from django.forms import widgets


# Add your forms here
class CheckInForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    dob = forms.DateField(required=True)  # dob = Date of Birth: 02/14/1988 ToDo: format check
    ssn = forms.CharField(max_length=9)  # ToDo: format check
    walk_in = forms.BooleanField(required=True)


class PatientUpdateProfileForm(forms.Form):
    email = forms.EmailField(required=False)
    dob = forms.DateField(required=True)  # dob = Date of Birth: 02/14/1988 ToDo: format check
    street_address = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=5, required=True)
    state = forms.CharField(max_length=5, required=True)
    home_phone = forms.CharField(max_length=15, required=True)  # ToDo: format check
    cell_phone = forms.CharField(max_length=15, required=False)   # ToDo: format check
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_phone = forms.CharField(max_length=15, required=False)  # ToDo: format check
