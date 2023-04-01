from django.contrib import admin
from .models import profile_image
from .models import camera_model

# Register your models here.

admin.site.register(profile_image)
admin.site.register(camera_model)

class  image_admin(admin.ModelAdmin):
    list_display = ['id','photo', 'roll_num', 'name', 'department', 'semester', 'status']

class  camera_admin(admin.ModelAdmin):
    list_display = ['Main_id','cam_id','ip', 'location', 'note']