from django.contrib import admin
from django.urls import path, include
from .views import login_view, home, register_view, logout_view, model_form_upload, download_files
from django.conf.urls.static import static
from django.conf import settings

app_name = "core"

urlpatterns = [
    path('', model_form_upload, name="home"),
    path('login/', login_view, name="login"),
    path('register/', register_view, name="register"),
    path('logout/', logout_view, name="logout"),
    path('upload/', model_form_upload, name="upload"),
    path('download/', download_files, name="download")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)