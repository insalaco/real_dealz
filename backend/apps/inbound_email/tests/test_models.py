import pytest
from django.utils import timezone
from apps.inbound_email.models import InboundEmail

@pytest.mark.django_db
def test_inbound_email_creation(saved_inbound_email):
    email = saved_inbound_email

    assert email.message_id == "test-message-id-123"
    assert email.sender == "sender@example.com"
    assert email.recipient == "recipient@example.com"
    assert email.subject == "Test Subject"
    assert email.body_plain == "This is the plain text body"
    assert email.body_html == "<p>This is HTML body</p>"
    assert email.is_processed is False
    assert email.processed_at is None

@pytest.mark.django_db
def test_inbound_email_str(saved_inbound_email):
    email = saved_inbound_email
    expected = f"{email.subject} from {email.sender}"
    assert str(email) == expected

@pytest.mark.django_db
def test_unique_message_id(db):
    email1 = InboundEmail.objects.create(
        message_id="unique-id-001",
        sender="a@example.com",
        recipient="b@example.com",
    )

    with pytest.raises(Exception):
        InboundEmail.objects.create(
            message_id="unique-id-001",
            sender="c@example.com",
            recipient="d@example.com",
        )

@pytest.mark.django_db
def test_mark_as_processed(saved_inbound_email):
    email = saved_inbound_email
    email.is_processed = True
    email.processed_at = timezone.now()
    email.save()

    email.refresh_from_db()
    assert email.is_processed is True
    assert email.processed_at is not None

