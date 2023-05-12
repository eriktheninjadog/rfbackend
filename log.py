from settings import settings

def log(msg):
    if settings['log']:
       print("Log: " + str(msg))
