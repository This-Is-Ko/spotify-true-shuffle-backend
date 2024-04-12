# Bind to the appropriate host and port
bind = '0.0.0.0:443'

# Path to SSL certificate file
certfile = '/ssl/fullchain.pem'

# Path to SSL private key file
keyfile = '/ssl/privkey.pem'

# Number of Gunicorn worker processes
workers = 3

timeout = 60