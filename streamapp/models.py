from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

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


# Create your models here.

class profile_image(models.Model):
    id = models.AutoField(primary_key=True)
    # --user being added
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_images', null=True)
    
    photo = models.ImageField(upload_to="profile_images", default="")
    roll_num = models.IntegerField(blank= True, null=False, unique=True, validators=[MinValueValidator(1)])
    name = models.CharField(max_length=122, default="None", blank= True, null=True, validators=[RegexValidator(r'^[a-zA-Z\s]*$', 'Only alphabets are allowed.')])
    department = models.CharField(max_length=122, default="None", blank= True, null=True)
    semester = models.CharField(max_length=122, default="None", blank= True, null=True )
    status = models.CharField(max_length=122, default="None", blank= True, null=True )


class camera_model(models.Model):
    Main_id = models.AutoField(primary_key=True)
    cam_id = models.IntegerField(blank= True, null=True, unique=True)
    ip  = models.CharField(max_length=122, default="None", blank= True, null=True)
    location = models.CharField(max_length=122, default="None", blank= True, null=True)
    note = models.CharField(max_length=122, default="None", blank= True, null=True)


class settings_model(models.Model):
    id_settings = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    attendance_update_time_min = models.IntegerField(blank= True, null=True, default=30, validators=[MinValueValidator(1)])
    head_turn_count =  models.IntegerField(blank= True, null=True, default=7, validators=[MinValueValidator(1), MaxValueValidator(100)])
    head_count_time_sec = models.IntegerField(blank= True, null=True, default=60, validators=[MinValueValidator(1), MaxValueValidator(3600)])
    left_head_threshHold = models.IntegerField(blank= True, null=True, default=-6, validators=[MaxValueValidator(-1), MinValueValidator(-50)])
    right_head_threshHold = models.IntegerField(blank= True, null=True, default=6, validators=[MinValueValidator(1), MaxValueValidator(50)])