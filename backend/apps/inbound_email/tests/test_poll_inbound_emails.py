import pytest
from unittest.mock import patch, Mock
from django.core.management import call_command
from apps.inbound_email.models import InboundEmail


@pytest.mark.django_db
def test_poll_inbound_emails_creates_new_emails():
    """Test that the command creates new InboundEmail objects from Mailgun events."""

    fake_response = {
        "items": [
            {
                "message": {
                    "headers": {
                        "message-id": "msg-123",
                        "from": "alice@example.com",
                        "to": "bob@example.com",
                        "subject": "Hello",
                    },
                    "body-plain": "Plain text",
                    "body-html": "<p>HTML</p>",
                    "mime": "raw mime",
                }
            },
            {
                "message": {
                    "headers": {
                        "message-id": "msg-456",
                        "from": "charlie@example.com",
                        "to": "dave@example.com",
                        "subject": "World",
                    },
                    "body-plain": "Another plain text",
                    "body-html": "<p>Another HTML</p>",
                    "mime": "raw mime 2",
                }
            },
        ]
    }

    with patch("requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_response
        mock_get.return_value = mock_resp

        call_command("poll_inbound_emails")

    # Assert emails are saved
    assert InboundEmail.objects.count() == 2
    email1 = InboundEmail.objects.get(message_id="msg-123")
    assert email1.sender == "alice@example.com"
    assert email1.subject == "Hello"
    assert email1.body_plain == "Plain text"

    email2 = InboundEmail.objects.get(message_id="msg-456")
    assert email2.sender == "charlie@example.com"
    assert email2.subject == "World"


@pytest.mark.django_db
def test_poll_inbound_emails_skips_existing_email(saved_inbound_email):
    """Test that already existing emails are skipped."""
    
    fake_response = {
        "items": [
            {
                "message": {
                    "headers": {
                        "message-id": saved_inbound_email.message_id,
                        "from": saved_inbound_email.sender,
                        "to": saved_inbound_email.recipient,
                        "subject": saved_inbound_email.subject,
                    },
                    "body-plain": saved_inbound_email.body_plain,
                    "body-html": saved_inbound_email.body_html,
                    "mime": saved_inbound_email.raw_mime,
                }
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_response
        mock_get.return_value = mock_resp

        call_command("poll_inbound_emails")

    # Should not create a duplicate
    assert InboundEmail.objects.count() == 1
