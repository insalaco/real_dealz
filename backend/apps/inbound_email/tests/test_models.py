import pytest
from django.utils import timezone
from apps.inbound_email.models import InboundEmail, EmailAttachment

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

# ----------------------------
# Tests for EmailAttachment
# ----------------------------

@pytest.mark.django_db
def test_email_attachment_creation(saved_inbound_email):
    email = saved_inbound_email
    attachment = EmailAttachment.objects.create(
        email=email,
        filename="test_image.png",
        s3_url="https://bucket.s3.amazonaws.com/test_image.png",
        content_type="image/png"
    )

    assert attachment.email == email
    assert attachment.filename == "test_image.png"
    assert attachment.s3_url.startswith("https://")
    assert attachment.content_type == "image/png"

@pytest.mark.django_db
def test_email_attachment_str(saved_inbound_email):
    email = saved_inbound_email
    attachment = EmailAttachment.objects.create(
        email=email,
        filename="document.pdf",
        s3_url="https://bucket.s3.amazonaws.com/document.pdf",
        content_type="application/pdf"
    )

    expected_str = f"{attachment.filename} ({email})"
    assert str(attachment) == expected_str

@pytest.mark.django_db
def test_email_attachments_relationship(saved_inbound_email):
    email = saved_inbound_email
    att1 = EmailAttachment.objects.create(
        email=email,
        filename="file1.txt",
        s3_url="https://bucket.s3.amazonaws.com/file1.txt"
    )
    att2 = EmailAttachment.objects.create(
        email=email,
        filename="file2.txt",
        s3_url="https://bucket.s3.amazonaws.com/file2.txt"
    )

    attachments = list(email.attachments.all())
    assert len(attachments) == 2
    assert att1 in attachments
    assert att2 in attachments
