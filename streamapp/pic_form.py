from django import forms
from .models import profile_image, camera_model, settings_model
from django.contrib.auth.models import User


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

class settings_form(forms.ModelForm):

    id_settings = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
    }))

    # -- user is being built here
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={
        "class": "form-control",
    }), label='User')

    attendance_update_time_min = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "After how many minutes attendance is saved",
    }))

    head_turn_count = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "No of times a person turns head and gets pictured",
    }))

    head_count_time_sec = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "Head turn counts resets every __ secounds",
    }))

    left_head_threshHold = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "-ve only, Left angle till which one can look",
    }))

    right_head_threshHold = forms.IntegerField(widget= forms.NumberInput(attrs={
        "class" : "form-control",
        "placeholder" : "+ve only, Right angle till which one can look",
    }))



    class Meta:
        model = settings_model
        fields = '__all__'
        