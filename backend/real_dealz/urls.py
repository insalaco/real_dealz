from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inbound_email/', include('apps.inbound_email.urls')),
]
