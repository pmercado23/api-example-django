from django import forms
from django.forms import widgets


# Add your forms here
class CheckInForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    date = forms.DateField(
        label="Date Of Birth",
        widget=forms.SelectDateWidget(years=range(1900, 2020)))
    ssn = forms.CharField(label='SSN', max_length=11)  # ToDo: format check
    walk_in = forms.BooleanField(label='Walk-In?', required=False)

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
    ("declined", "Declined")
)

class PatientDemographicForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=150, required=True)
    last_name = forms.CharField(label='Last Name', max_length=150, required=True)
    date_of_birth = forms.DateField(
        label="Date Of Birth",
        widget=forms.SelectDateWidget(years=range(1900, 2021)))
    gender = forms.ChoiceField(label='Gender', choices=GENDER_CHOICES, required=True)
    email = forms.CharField(label='Email', max_length=150, required=False)
    race = forms.ChoiceField(label='Race', choices=RACE_CHOICES, required=False)
    ethnicity = forms.ChoiceField(label='Ethnicity', choices=ETHNICITY_CHOICES, required=False)
    preferred_language = forms.ChoiceField(label='Preferred Language', choices=LANG_CHOICES, required=False)
