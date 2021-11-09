import json
import time
import requests
import logging

logfile = 'log_1.log'

log = logging.getLogger("my_log")
log.setLevel(logging.INFO)
FH = logging.FileHandler(logfile)
basic_formater = logging.Formatter('%(asctime)s : [%(levelname)s] : %(message)s')
FH.setFormatter(basic_formater)
log.addHandler(FH)


URL_SOURCE = 'https://apps.lukashenkopresidentnet.online/bot.php?zenkRequest=get_all_apps&secret=~6KBsKMPhS2Y'
BASE_URL = 'http://127.0.0.1:3458/api'
START_APP = '393313022536314'


def get_source():
    data = []
    response = requests.get(url=URL_SOURCE, verify=False)
    response = response.text.split(';')
    if len(response) == 1:
        return None
    for res in response:
        obj_dict = res.split(',')
        obj = {}
        obj['name'] = obj_dict[0]
        obj['id'] = obj_dict[1]
        data.append(obj)
    return data


def get_all_apps():
    responce = requests.get(BASE_URL + '/all_apps')
    if responce.status_code == 200:
        return responce.json()
    return None

def send_state_in_account(state):
    headers = {'Content-Type': 'application/json'}
    responce = requests.post(f'{BASE_URL}/send_ids',headers=headers,json=state,verify=False)
    return responce

def get_current_state_apps():
    apps = get_all_apps()
    data = []
    for app in apps:
        url = f'{BASE_URL}/get_ids?id_app={str(app["id"])}'
        res = requests.get(url)
        data.append(res.json())
        time.sleep(3)
    return data

def reload_local_state_apps():
    state = get_current_state_apps()
    with open('state_apps.json','w') as writer:
        writer.write(str(state).replace("'",'"'))

def update_local_state_apps(state):
    with open('state_apps.json','w') as writer:
        writer.write(str(state).replace("'",'"'))

def local_state():
    with open('state_apps.json','r') as reader:
        data = json.loads(reader.read())
    return data

if __name__ == '__main__':
    while 1:
        local_s = local_state()
        log.info('Send request')
        log.info(f'local state {str(local_s)}')
        new_state = get_source()
        log.info(f'Source {str(new_state)}')
        if new_state == None:
            print('Not update')
            continue
        for new_app in new_state:
            for local_app in local_s:

                if new_app['name'] == local_app['appname']:
                    tmp = local_app['data']
                    tmp.append(new_app['id'])
                    tmp = set(tmp)
                    local_app['data'] = list(tmp)
        logging.info(f'New state {str(local_s)}')
        res = send_state_in_account(local_s)
        logging.info(f'Responce {res.text}')
        update_local_state_apps(local_s)
        time.sleep(60)


