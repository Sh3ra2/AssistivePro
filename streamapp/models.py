from django.db import models


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
    photo = models.ImageField(upload_to="profile_images", default="")
    roll_num = models.IntegerField(blank= True, null=False, unique=True)
    name = models.CharField(max_length=122, default="None", blank= True, null=True)
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
    id_settings = models.IntegerField(blank= True, null=True, unique=True, default=1)
    attendance_update_time_min = models.IntegerField(blank= True, null=True, unique=True, default=30)
    head_turn_count =  models.IntegerField(blank= True, null=True, unique=True, default=7)
    head_count_time_sec = models.IntegerField(blank= True, null=True, unique=True, default=60)
    left_head_threshHold = models.IntegerField(blank= True, null=True, unique=True, default=-6)
    right_head_threshHold = models.IntegerField(blank= True, null=True, unique=True, default=6)