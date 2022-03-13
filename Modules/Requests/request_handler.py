import json

def check_for_file():
    try:
        with open('./Modules/Requests/requests.txt', 'r') as f:
            pass
    except:
        with open('./Modules/Requests/requests.txt', 'x') as f:
            f.seek(0)
            f.write('[]')
            return

def add_request(request_info: dict):
    check_for_file()
    with open('./Modules/Requests/requests.txt', 'a+') as f:
        f.seek(0)
        current_list = json.loads(f.read())
        current_list.append(request_info)

        f.truncate(0)

        f.write(json.dumps(current_list, indent=2, separators=(',', ':')))