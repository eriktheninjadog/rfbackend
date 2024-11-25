#config

import json
def get_config_value(name):
    f = open('/home/erik/wwwconfig.json','r')
    dict = json.loads(f.read())
    f.close()
    return dict[name]