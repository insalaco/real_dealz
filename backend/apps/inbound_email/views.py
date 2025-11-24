import hashlib
import hmac
import logging
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import InboundEmail

logger = logging.getLogger(__name__)


def verify_mailgun_signature(token, timestamp, signature):
    """Verify that the webhook is actually from Mailgun"""
    signing_key = getattr(settings, 'MAILGUN_WEBHOOK_SIGNING_KEY', settings.MAILGUN_API_KEY)
    hmac_digest = hmac.new(
        key=signing_key.encode(),
        msg=f'{timestamp}{token}'.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, hmac_digest)


@method_decorator(csrf_exempt, name='dispatch')
class MailInboundView(View):
    def post(self, request, *args, **kwargs):
        # Log incoming request for debugging
        logger.info("=" * 80)
        logger.info(f"Received webhook request")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info("=" * 80)

        # Verify signature for security
        token = request.POST.get('token')
        timestamp = request.POST.get('timestamp')
        signature = request.POST.get('signature')

        if token and timestamp and signature:
            if not verify_mailgun_signature(token, timestamp, signature):
                logger.warning("Invalid Mailgun webhook signature")
                logger.warning(f"Token: {token}, Timestamp: {timestamp}, Signature: {signature}")
                return JsonResponse({"error": "Invalid signature"}, status=403)
        else:
            logger.warning("Missing signature data in webhook")
            logger.warning(f"Token: {token}, Timestamp: {timestamp}, Signature: {signature}")

        # Extract email data
        message_id = request.POST.get('Message-Id')
        sender = request.POST.get('From') or request.POST.get('sender')
        recipient = request.POST.get('To') or request.POST.get('recipient')
        subject = request.POST.get('Subject') or request.POST.get('subject')
        body_plain = request.POST.get('body-plain') or request.POST.get('stripped-text')
        body_html = request.POST.get('body-html') or request.POST.get('stripped-html')

        logger.info(f"Message-Id: {message_id}")
        logger.info(f"Subject: {subject}")
        logger.info(f"From: {sender}")
        logger.info(f"To: {recipient}")
        logger.info(f"Body plain length: {len(body_plain) if body_plain else 0}")
        logger.info(f"Body html length: {len(body_html) if body_html else 0}")

        if not message_id:
            logger.warning("Received webhook without Message-Id")
            return HttpResponse("No Message-Id", status=200)  # Return 200 to avoid retries

        # Check if already exists
        if InboundEmail.objects.filter(message_id=message_id).exists():
            logger.info(f"Email {message_id} already exists, skipping")
            return HttpResponse("Duplicate", status=200)

        # Create email record
        try:
            email_obj = InboundEmail.objects.create(
                message_id=message_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                body_plain=body_plain,
                body_html=body_html,
                raw_mime=None,
                metadata=dict(request.POST),
                is_processed=False,
            )
            logger.info(f"✅ Created email record {email_obj.id} for message {message_id}")
        except Exception as e:
            logger.error(f"❌ Error creating email record: {e}", exc_info=True)
            return HttpResponse("Error saving email", status=200)

        logger.info(f"✅ Successfully processed inbound email {message_id}")
        return HttpResponse("Received", status=200)
