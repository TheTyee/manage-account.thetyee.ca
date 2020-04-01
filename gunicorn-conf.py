def post_fork(server, worker):
    app.logger.info("gunicorn - post_fork")
    client = recurly.Client(app.config['RECURLY_KEY'])