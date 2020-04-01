import os
import recurly

def post_fork(server, worker):
    client = recurly.Client(os.environ['RECURLY_KEY'])