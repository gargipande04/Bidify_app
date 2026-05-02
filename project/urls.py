from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve

from api import views

urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("health", lambda request: HttpResponse("OK")),
    path("", views.main_spa),
]

# Serve uploaded media files (works with DEBUG=False)
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

# SPA fallback 
urlpatterns += [
    re_path(r"^(?!api/|media/|admin/).*$", views.main_spa),
]
