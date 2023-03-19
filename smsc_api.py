import time
from contextvars import ContextVar
from typing import Optional

import asks
import trio

smsc_login: ContextVar[str] = ContextVar('smsc_login')
smsc_password: ContextVar[str] = ContextVar('smsc_password')


class SmscApiError(Exception):
    pass


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

async def request_smsc(
        http_method: str,
        api_method: str,
        *,
        login: Optional[str] = None,
        password: Optional[str] = None,
        payload: dict = {}
) -> dict:
    """Send request to SMSC.ru service.

    Args:
        http_method (str): E.g. 'GET' or 'POST'.
        api_method (str): E.g. 'send' or 'status'.
        login (str): Login for account on smsc.ru.
        password (str): Password for account on smsc.ru.
        payload (dict): Additional request params, override default ones.
    Returns:
        dict: Response from smsc.ru API.
    Raises:
        SmscApiError: If smsc.ru API response status is not 200 or JSON response
        has "error_code" inside.

    Examples:
        >>> await request_smsc(
        ...   'POST',
        ...   'send',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={'phones': '+79123456789'}
        ... )
        {'cnt': 1, 'id': 24}
        >>> await request_smsc(
        ...   'GET',
        ...   'status',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={
        ...     'phone': '+79123456789',
        ...     'id': '24',
        ...   }
        ... )
        {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
    """
    login = login or smsc_login.get()
    password = password or smsc_password.get()
    response_format = 3
    params = {
        'login': login,
        'psw': password,
        # 'phones': phones,
        # 'mes': msg,
        # 'valid': msg_lifetime,
        'fmt': response_format,
    }
    params.update(payload)

    url = f'https://smsc.ru/sys/{api_method}.php'
    if http_method == 'GET' and api_method == 'status':
        if not params.get('phones', None):
            raise SmscApiError('phones not specified')
        if not params.get('mes', None):
            raise SmscApiError('mes not specified')

    elif http_method == 'POST' and api_method == 'send':
        if not params.get('phone', None):
            raise SmscApiError('phone not specified')
        if not params.get('id', None):
            raise SmscApiError('id not specified')
    else:
        raise SmscApiError("api method doesn't exist")

    response = await asks.request(http_method, url, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    print(decoded_response)


if __name__ == "__main__":
    smsc_login.set('syncmas')
    smsc_password.set('Simonat5931')
    # login = 'syncmas'
    # psw = 'Simonat5931'
    phones = '+77059648729, +79652943192'
    msg = 'test from api post8'
    msg_lifetime = 1
    trio.run(send_msg, login, psw, phones, msg, msg_lifetime)
