# apps/inbound_email/management/commands/poll_inbound_emails.py
import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.inbound_email.models import InboundEmail

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Poll Mailgun for stored inbound emails"

    def handle(self, *args, **options):
        domain = settings.MAILGUN_DOMAIN
        api_key = settings.MAILGUN_API_KEY
        base_url = getattr(settings, "MAILGUN_API_BASE", "https://api.mailgun.net/v3")

        url = f"{base_url}/{domain}/events"

        self.stdout.write("Polling Mailgun stored inbound emails...")

        params = {
            "event": "stored",
            "limit": 300,
        }

        try:
            response = requests.get(url, auth=("api", api_key), params=params)
        except Exception as exc:
            logger.error(f"Error connecting to Mailgun: {exc}")
            return

        if response.status_code != 200:
            logger.error(f"Mailgun error {response.status_code}: {response.text}")
            return

        data = response.json()
        items = data.get("items", [])

        logger.info(f"Fetched {len(items)} stored events from Mailgun.")

        new_count = 0
        skipped_count = 0

        for event in items:
            message = event.get("message", {})
            message_id = message.get("headers", {}).get("message-id")

            if not message_id:
                logger.warning("Skipping event with no message-id.")
                continue

            if InboundEmail.objects.filter(message_id=message_id).exists():
                skipped_count += 1
                continue

            # Save the email
            InboundEmail.objects.create(
                message_id=message_id,
                sender=message.get("headers", {}).get("from", ""),
                recipient=message.get("headers", {}).get("to", ""),
                subject=message.get("headers", {}).get("subject"),
                body_plain=message.get("body-plain"),
                body_html=message.get("body-html"),
                raw_mime=message.get("mime"),
                metadata=event,
                is_processed=False,
            )

            new_count += 1

        logger.info(f"Saved {new_count} new emails.")
        logger.info(f"Skipped {skipped_count} already-saved emails.")

        self.stdout.write(
            self.style.SUCCESS(f"Done. New: {new_count}, Skipped: {skipped_count}")
        )
