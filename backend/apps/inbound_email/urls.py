from django.urls import path
from .views import MailInboundView

urlpatterns = [
    # ...existing code...
    path('inbound/', MailInboundView.as_view(), name='mail_inbound'),
]