from django.contrib import admin
from .models import profile_image
from .models import camera_model, settings_model

# Register your models here.

admin.site.register(profile_image)
admin.site.register(camera_model)
admin.site.register(settings_model)

class  image_admin(admin.ModelAdmin):
    list_display = ['id','photo', 'roll_num', 'name', 'department', 'semester', 'status']

class  camera_admin(admin.ModelAdmin):
    list_display = ['Main_id','cam_id','ip', 'location', 'note']

class  settings_admin(admin.ModelAdmin):
    list_display = ['id_settings', 'attendance_update_time', 'head_turn_count', 'head_count_time_sec', 'left_head_threshHold', 'right_head_threshHold']