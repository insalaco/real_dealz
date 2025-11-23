import pytest
from apps.inbound_email.models import InboundEmail
from django.utils import timezone


@pytest.fixture
def inbound_email():
    """
    Returns a single InboundEmail instance (not saved to DB).
    """
    return InboundEmail(
        message_id="test-message-id-123",
        sender="sender@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body_plain="This is the plain text body",
        body_html="<p>This is HTML body</p>",
        raw_mime="Raw MIME content",
        metadata={"test": "metadata"},
        received_at=timezone.now(),
        is_processed=False,
    )


@pytest.fixture
def saved_inbound_email(db, inbound_email):
    """
    Saves the inbound_email fixture to the database.
    """
    inbound_email.save()
    return inbound_email
