import time

import asks
import trio


async def send_msg(login, psw, phones, msg, msg_lifetime):
    start_time = time.time()
    response_format = 3
    params = {
        'login': login,
        'psw': psw,
        'phones': phones,
        'mes': msg,
        'valid': msg_lifetime,
        'fmt': response_format,
    }
    url = 'https://smsc.ru/sys/send.php'
    response = await asks.post(url, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    print(decoded_response)

    url = 'https://smsc.ru/sys/status.php'
    phones_count = len(phones.split(','))
    msg_ids = [decoded_response['id']] * phones_count
    params['id'] = ','.join(map(str, msg_ids))
    params = {
        'login': login,
        'psw': psw,
        'phone': phones,
        'id': ','.join(map(str, msg_ids)),
        'fmt': response_format,
    }
    response = await asks.get(url, params=params)
    decoded_response = response.json()
    print(decoded_response)

    print("Total time:", time.time() - start_time)


# [
#     {'status': 25, 'last_date': '17.03.2023 16:47:56', 'last_timestamp': 1679060876, 'flag': 0, 'err': 248, 'id': 32,
#      'phone': '77059648729'},
#     {'status': 23, 'last_date': '17.03.2023 16:47:56', 'last_timestamp': 1679060876, 'flag': 0, 'err': 254, 'id': 32,
#      'phone': '79652943192'}
# ]

# 'https://smsc.ru/sys/status.php?login=syncmas&psw=Simonat5931&phone=+79052943192,+77059648729&fmt=3&id=16,16'
# 'https://smsc.ru/sys/send.php?login=syncmas&psw=Simonat5931&phones=+77059648729,+79052943192&mes=test%20message%20from%20api&op=1&fmt=3'

if __name__ == "__main__":
    login = 'syncmas'
    psw = 'Simonat5931'
    phones = '+77059648729, +79652943192'
    msg = 'test from api post8'
    msg_lifetime = 1
    trio.run(send_msg, login, psw, phones, msg, msg_lifetime)
