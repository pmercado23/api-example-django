from django import forms
from django.forms import widgets


# Add your forms here
class CheckInForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    dob = forms.CharField(required=True, max_length=10)  # dob = Date of Birth: 02/14/1988 ToDo: format check
    ssn = forms.CharField(max_length=11)  # ToDo: format check
    walk_in = forms.BooleanField(required=False)


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


# Below are Choices for demographic form

RACE_CHOICES = (
    ("blank", ""),
    ("indian", "American Indian or Alaska Native"),
    ("asian", "Asian"),
    ("black", "Black or African American"),
    ("hawaiian", "Native Hawaiian or Other Pacific Islander"),
    ("white", "White"),
    ("other", "Other Race"),
    ("declined", "Declined to specify"),
)

ETHNICITY_CHOICES = (
    ("blank", ""),
    ("hispanic", "Hispanic or Latino"),
    ("not_hispanic", "Not Hispanic or Latino"),
    ("declined", "Declined")
)

GENDER_CHOICES = (
    ("", ""),
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other")
)


LANG_CHOICES = (
    ("blank", ""),
    ("eng", "English"),
    ("zho", "Chinese"),
    ("fra", "French"),
    ("ita", "Italian"),
    ("jpn", "Japanese"),
    ("por", "Portuguese"),
    ("rus", "Russian"),
    ("spa", "Spanish"),
    ("other", "Other/See Notes"),
    ("unknown", "Unknown"),
    ("declined", "Declined"),

)

class PatientDemographicForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    date_of_birth = forms.CharField(max_length=150, required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    email = forms.CharField(max_length=150, required=False)
    race = forms.ChoiceField(choices=RACE_CHOICES, required=False)
    ethnicity = forms.ChoiceField(choices=ETHNICITY_CHOICES, required=False)
    preferred_language = forms.ChoiceField(choices=LANG_CHOICES, required=False)
