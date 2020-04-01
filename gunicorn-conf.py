import configparser
import recurly

config = configparser.ConfigParser()
config.read('settings.cfg')

def post_fork(server, worker):
    client = recurly.Client(config.get('RECURLY_KEY'))