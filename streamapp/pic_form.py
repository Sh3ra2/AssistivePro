from django import forms
from .models import profile_image
from .models import camera_model


DEPARTMENT_CHOICES = [
    ('IT', 'IT'),
    ('SE', 'SE'),
    ('Law', 'Law'),
    ('Aerospace', 'Aerospace'),
    ('English', 'English'),
    ('Zoology', 'Zoology'),
    ('Chemistry', 'Chemistry'),
    ('CS', 'CS'),
]
SEMESTER_CHOICES = [
    ( '1', '1' ),
    ( '2', '2' ),
    ( '3', '3' ),
    ( '4', '4' ),
    ( '5', '5' ),
    ( '6', '6' ),
    ( '7', '7' ),
    ( '8', '8' ),
]
STATUS_CHOICES = [
    ('Eligible', 'Eligible'),
    ('Not-Eligible', 'Not-Eligible'),
]

class image_form(forms.ModelForm):

    roll_num = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter Roll Number",
    }),label='Roll Number:')

    name = forms.CharField(widget= forms.TextInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter Name",
    }),label='Name:')

    department = forms.ChoiceField(widget= forms.Select(attrs={
        "class" : "form-control",
        "placeholder" : "Select Department",
    }),label='Department:', choices=DEPARTMENT_CHOICES)

    semester = forms.ChoiceField(widget= forms.Select(attrs={
        "class" : "form-control",
        "placeholder" : "Select semester",
    }),label='Semester:', choices=SEMESTER_CHOICES)

    status = forms.ChoiceField(widget= forms.Select(attrs={
        "class" : "form-control",
        "placeholder" : "Select Status",
    }),label='Status:', choices=STATUS_CHOICES)

    class Meta:
        model = profile_image
        fields = '__all__'


class camera_form(forms.ModelForm):

    cam_id = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter ID",
    }),label='Roll Number:')

    ip = forms.CharField(widget= forms.TextInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter IP",
    }),label='Name:')

    location = forms.CharField(widget= forms.TextInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter location",
    }),label='Name:')

    note = forms.CharField(widget= forms.TextInput(attrs={
        "class" : "form-control",
        "placeholder" : "Enter note",
    }),label='Name:')


    class Meta:
        model = camera_model
        fields = '__all__'