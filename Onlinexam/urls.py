from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from main import views
from froala_editor import views as froala_views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('student/', views.guestStudent, name='guestStudent'),
    path('teacher/', views.guestFaculty, name='guestFaculty'),
    path('', include('main.urls')),
    path('', include('discussion.urls')),

    path('', include('exam.urls')),
    path('froala_editor/', include('froala_editor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

