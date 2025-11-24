import io
import pytest
from django.urls import reverse
from apps.inbound_email.models import InboundEmail


@pytest.mark.django_db
def test_webhook_creates_email(client, mailgun_signature):
    url = reverse("mail_inbound")

    payload = {
        "Message-Id": "abc123",
        "From": "john@example.com",
        "To": "team@example.com",
        "Subject": "Hello",
        "body-plain": "Plain text",
        "body-html": "<p>Hello!</p>",
        "token": "t",
        "timestamp": "123",
        "signature": "sig",
    }

    response = client.post(url, data=payload)

    assert response.status_code == 200
    assert InboundEmail.objects.count() == 1

    email = InboundEmail.objects.first()
    assert email.message_id == "abc123"
    assert email.sender == "john@example.com"
    assert email.subject == "Hello"


@pytest.mark.django_db
def test_webhook_invalid_signature(client, monkeypatch):
    url = reverse("mail_inbound")

    # Force failure of signature
    from apps.inbound_email import views
    monkeypatch.setattr(views, "verify_mailgun_signature", lambda t, ts, s: False)

    payload = {
        "Message-Id": "abc123",
        "token": "t",
        "timestamp": "123",
        "signature": "BAD",
    }

    response = client.post(url, data=payload)

    assert response.status_code == 403
    assert InboundEmail.objects.count() == 0


@pytest.mark.django_db
def test_webhook_missing_message_id(client, mailgun_signature):
    url = reverse("mail_inbound")

    payload = {
        "From": "a@example.com",
        "To": "b@example.com",
        "token": "t",
        "timestamp": "123",
        "signature": "sig",
    }

    response = client.post(url, data=payload)

    # Should not error; should ignore and not save anything
    assert response.status_code == 200
    assert InboundEmail.objects.count() == 0


@pytest.mark.django_db
def test_webhook_duplicate_message_id(client, saved_inbound_email, mailgun_signature):
    url = reverse("mail_inbound")

    payload = {
        "Message-Id": saved_inbound_email.message_id,
        "token": "t",
        "timestamp": "123",
        "signature": "sig",
    }

    response = client.post(url, data=payload)

    assert response.status_code == 200
    assert InboundEmail.objects.count() == 1  # Still just 1 existing record


@pytest.mark.django_db
def test_webhook_with_attachment_ignored(client, mailgun_signature):
    """
    Since attachment logic is removed, files must be ignored.
    """
    url = reverse("mail_inbound")

    file_content = b"hello world"
    file = io.BytesIO(file_content)
    file.name = "hello.txt"

    payload = {
        "Message-Id": "with-file-123",
        "From": "john@example.com",
        "To": "team@example.com",
        "Subject": "Attachment Test",
        "attachment-count": "1",
        "token": "t",
        "timestamp": "123",
        "signature": "sig",
    }

    response = client.post(
        url,
        data=payload,
        files={"attachment-1": file},  # Should be ignored
    )

    assert response.status_code == 200
    assert InboundEmail.objects.count() == 1

    # No attachments saved anymore
    # EmailAttachment model no longer used; test should not reference it
