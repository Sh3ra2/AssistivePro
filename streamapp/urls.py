from django.urls import path, include
from streamapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


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
    path('recent_att', views.recent_att, name='recent_att'),
    path('edit_student/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
    path('delete_csv/<str:file_name>/', views.delete_csv, name='delete_csv'),
    path('app_settings', views.app_settings, name='app_settings'),
    path('end_session', views.end_session, name='end_session'),
    path('end_session_att', views.end_session_att, name='end_session_att'),
    path('add_user', views.add_user, name='add_user'),
    path('user_view', views.user_view, name='user_view'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('delete_user/<str:id>', views.delete_user, name='delete_user'),
    path('edit_user/<str:id>', views.edit_user, name='edit_user'),
    
    # -- browser tab bar logo
    path(
        'favicon.ico',
        RedirectView.as_view(url=staticfiles_storage.url('images/logoAssistivePro.ico')),
        name='favicon'
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
