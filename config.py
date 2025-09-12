#config
# eoo
import json
def get_config_value(name):
    f = open('/var/www/html/scene/wwwconfig.json','r')
    dict = json.loads(f.read())
    f.close()
    return dict[name]