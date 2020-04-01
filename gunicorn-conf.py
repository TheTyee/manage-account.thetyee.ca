import recurly

def post_fork(server, worker):
    #log.debug("gunicorn - post_fork")
    client = recurly.Client(app.config['RECURLY_KEY'])