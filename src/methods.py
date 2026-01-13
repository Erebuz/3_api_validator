import datetime
import hashlib
from typing import Any

from src.constants import ADMIN_SALT, SALT
from src.datas import OnlineScoreRequest, ClientsInterestsRequest, MethodRequest


def check_auth(request: MethodRequest) -> bool:
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()

    return digest == request.token

def get_validate_online_score(arguments: dict[str, Any]) -> tuple[OnlineScoreRequest | list[str], list[str]]:
    score = OnlineScoreRequest()

    errors = []
    has = []

    for key in dir(OnlineScoreRequest):
        if not key.startswith('__'):
            try:
                value = arguments.get(key, None)
                setattr(score, key, value)
                if value is not None:
                    has.append(key)
            except ValueError:
                errors.append(f'Incorrect {key} value')
    if len(errors) > 0:
        return errors, has
    else:
        phone = arguments.get('phone', None)
        email = arguments.get('email', None)
        birthday = arguments.get('birthday', None)
        gender = arguments.get('gender', None)
        first_name = arguments.get('first_name', None)
        last_name = arguments.get('last_name', None)

        if ((phone is not None and email is not None)
                or (birthday is not None  and gender is not None )
                or (first_name is not None  and last_name is not None )):
            return score, has
        else:
            return ['No couple'], has


def clients_interests_validator(arguments: dict[str, Any]):
    interests = ClientsInterestsRequest()

    errors = []
    nclients = len(arguments.get('client_ids', []))

    for key in dir(ClientsInterestsRequest):
        if not key.startswith('__'):
            try:
                value = arguments.get(key, None)
                setattr(interests, key, value)
            except ValueError:
                errors.append(f'Incorrect {key} value')
    if len(errors) > 0:
        return errors, nclients
    else:
        return interests, nclients
