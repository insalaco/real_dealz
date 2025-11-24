generate djano secret key
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

add ngrok url to .env allowed hosts
add ngrok url to mailgun routes
send emails to `*@inbound.followerfrenzy.com`

pip freeze > requirements.txt

python manage.py poll_inbound_emails

## NGROCK

ngrok http 8000

visit https://app.mailgun.com/mg/receiving/routes and paste ngrok url `<ngrok url>/inbound_email/inbound/`

update .env allowed hosts to incude same ngrok url (no https://)

## Subdomain to receive email

inbound.followerfrenzy.com
