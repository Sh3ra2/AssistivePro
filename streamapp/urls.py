from django.urls import path, include
from streamapp import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('video_feed', views.video_feed, name='video_feed'),
    path('monitor_students_feed', views.monitor_students_feed, name='monitor_students_feed'),
    path('', views.index, name='index'),
    path('video_data', views.video_data, name='video_data'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('new_data', views.new_data, name='new_data'),
    path('view_data', views.view_data, name='view_data'),
    path('encode_data', views.encode_data, name='encode_data'),
    path('pre_encode', views.pre_encode, name='pre_encode'),
    path('pre_session', views.pre_session, name='pre_session'),
    path('monitor_students', views.monitor_students, name='monitor_students'),
    path('camera_manage', views.camera_manage, name='camera_manage'),
    path('recent_att', views.recent_att, name='recent_att'),
    path('add_camera', views.add_camera, name='add_camera'),
    path('edit_student/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    path('deleteCamera/<int:id>/', views.delete_camera, name='delete_camera'),
    path('edit_camera/<int:id>/', views.edit_camera, name='edit_camera'),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
    path('delete_csv/<str:file_name>/', views.delete_csv, name='delete_csv'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
