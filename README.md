ngrok http 8000

generate djano secret key
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

add ngrok url to .env allowed hosts
add ngrok url to mailgun routes
send emails to `*@inbound.followerfrenzy.com`

pip freeze > requirements.txt
