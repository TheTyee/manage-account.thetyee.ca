import configparser
import recurly

config = ConfigParser.ConfigParser()
config.read('settings.cfg')

def post_fork(server, worker):
    client = recurly.Client(config.get('Section1', 'foo', 0))