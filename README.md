# manage-account.thetyee.ca

## Development

flask run -p 15002 

## Production

gunicorn -w 4 -b 127.0.0.1:15001 app:app