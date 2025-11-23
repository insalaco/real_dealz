from django.shortcuts import render

from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class MailInboundView(View):
    def post(self, request, *args, **kwargs):
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        body_plain = request.POST.get('body-plain')
        # You can process/store the email here
        print(f"Email from: {sender}, subject: {subject}, body: {body_plain}")
        return HttpResponse("Received", status=200)
