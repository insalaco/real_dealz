import pytest
from django.utils import timezone
from apps.inbound_email.models import InboundEmail


@pytest.fixture
def inbound_email():
    return InboundEmail(
        message_id="test-message-id-123",
        sender="sender@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body_plain="This is the plain text body",  # <-- updated
        body_html="<p>This is HTML body</p>", 
        raw_mime="raw",
        metadata={"key": "value"},
        received_at=timezone.now(),
        is_processed=False,
    )



@pytest.fixture
def saved_inbound_email(db, inbound_email):
    inbound_email.save()
    return inbound_email


@pytest.fixture
def mailgun_signature(monkeypatch):
    """
    Forces signature verification to pass for most tests.
    """
    from apps.inbound_email import views
    monkeypatch.setattr(views, "verify_mailgun_signature", lambda t, ts, s: True)
    return True
