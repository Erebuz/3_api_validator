import datetime
import hashlib
from contextlib import nullcontext as does_not_raise
from typing import Any, Counter

import pytest
from _pytest.raises import RaisesExc

from src.constants import ADMIN_LOGIN, ADMIN_SALT, SALT
from src.datas import ClientsInterestsRequest, MethodRequest, OnlineScoreRequest
from src.methods import check_auth, validate_clients_interests, validate_online_score


class TestCheckAuth:
    @staticmethod
    def create_method_request(request: dict[str, Any]) -> MethodRequest:
        req = MethodRequest()
        req.account = request.get("account")
        req.login = request.get("login")
        req.token = request.get("token")
        req.arguments = request.get("arguments")
        req.method = request.get("method")

        return req

    @staticmethod
    def get_valid_token(request: dict[str, Any]) -> str:
        if request.get("login") == ADMIN_LOGIN:
            return hashlib.sha512(
                (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")).hexdigest()
        else:
            msg = (request.get("account", "") + request.get("login", "") + SALT).encode("utf-8")
            return hashlib.sha512(msg).hexdigest()

    @pytest.mark.parametrize(
        "request_args",
        [
            (
                {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "token": "",
                    "arguments": {},
                }
            ),
            (
                {
                    "account": "horns&hoofs",
                    "login": "admin",
                    "method": "online_score",
                    "token": "",
                    "arguments": {},
                }
            ),
        ],
    )
    def test_check_auth_success(self, request_args: dict[str, Any]) -> None:
        token = self.get_valid_token(request_args)
        request_args["token"] = token
        req = self.create_method_request(request_args)

        assert check_auth(req)


    @pytest.mark.parametrize(
        "request_args",
        [
            (
                {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "token": "dssd",
                    "arguments": {},
                }
            ),
            (
                {
                    "account": "horns&hoofs",
                    "login": "admin",
                    "method": "online_score",
                    "token": "",
                    "arguments": {},
                }
            ),
        ],
    )
    def test_check_auth_invalid(self, request_args: dict[str, Any]) -> None:
        req = self.create_method_request(request_args)
        assert not check_auth(req)

class TestValidateOnlineScore:
    @pytest.mark.parametrize(
        "arguments, result_has",
        [
            ({"gender": 0, "birthday": "01.01.2000"}, ["gender", "birthday"]),
            ({"phone": "79175002040", "email": "stupnikov@otus.ru"}, ["phone", "email"]),
            ({"phone": 79175002040, "email": "stupnikov@otus.ru"}, ["phone", "email"]),
            (
                {
                    "gender": 1,
                    "birthday": "01.01.2000",
                    "first_name": "a",
                    "last_name": "b",
                },
                ["gender", "birthday", "first_name", "last_name"],
            ),
            ({"gender": 0, "birthday": "01.01.2000"}, ["gender", "birthday"]),
            ({"gender": 2, "birthday": "01.01.2000"}, ["gender", "birthday"]),
            ({"first_name": "a", "last_name": "b"}, ["first_name", "last_name"]),
            (
                {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "gender": 1,
                    "birthday": "01.01.2000",
                    "first_name": "a",
                    "last_name": "b",
                },
                ["phone", "email", "gender", "birthday", "first_name", "last_name"],
            ),
        ],
    )
    def test_validate_online_score_success(self, arguments: dict[str, Any], result_has: list[str]) -> None:
        result, has = validate_online_score(arguments)

        assert Counter(has) == Counter(result_has)
        assert isinstance(result, OnlineScoreRequest)


    @pytest.mark.parametrize(
        "arguments, result_has",
        [
            ({}, []),
            ({"phone": "79175002040"}, ["phone"]),
            ({"phone": "89175002040", "email": "stupnikov@otus.ru"}, ["email"]),
            ({"phone": "79175002040", "email": "stupnikovotus.ru"}, ["phone"]),
            ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1}, ["phone", "email"]),
            ({"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"}, ["phone", "email"]),
            (
                {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "gender": 1,
                    "birthday": "01.01.1890",
                },
                ["phone", "email", "gender"],
            ),
            (
                {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "gender": 1,
                    "birthday": "XXX",
                },
                ["phone", "email", "gender"],
            ),
            (
                {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "gender": 1,
                    "birthday": "01.01.2000",
                    "first_name": 1,
                },
                ["phone", "email", "gender", "birthday"],
            ),
            (
                {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "gender": 1,
                    "birthday": "01.01.2000",
                    "first_name": "s",
                    "last_name": 2,
                },
                ["phone", "email", "gender", "birthday", "first_name"],
            ),
            ({"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"}, ["phone", "birthday", "first_name"]),
            ({"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2}, ["email", "gender"]),
        ],
    )
    def test_validate_online_score_invalid(self, arguments: dict[str, Any], result_has: list[str]) -> None:
        result, has = validate_online_score(arguments)

        assert Counter(has) == Counter(result_has)
        assert isinstance(result, list)

class TestValidateClientsInterests:
    @pytest.mark.parametrize(
        "arguments, result_nclients",
        [
            ({"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}, 4),
            ({"client_ids": [1], "date": "20.07.2017"}, 1),
            ({"client_ids": [1]}, 1),
            ({"client_ids": [1], "date": ""}, 1),
        ],
    )
    def test_validate_clients_interests_success(self, arguments: dict[str, Any], result_nclients: int) -> None:
        result, nclients = validate_clients_interests(arguments)

        assert nclients == result_nclients
        assert isinstance(result, ClientsInterestsRequest)


    @pytest.mark.parametrize(
        "arguments, result_nclients, expectation",
        [
            ({"client_ids": [], "date": "20.07.2017"}, 0, does_not_raise()),
            ({"client_ids": 1, "date": "20.07.2017"}, 0, pytest.raises(TypeError)),
            ({"client_ids": {1: 1}, "date": "20.07.2017"}, 1, does_not_raise()),
            ({"client_ids": [1], "date": "20"}, 1, does_not_raise()),
        ],
    )
    def test_validate_clients_interests_invalid(self, arguments: dict[str, Any], result_nclients: int, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        with expectation:
            result, nclients = validate_clients_interests(arguments)

            assert nclients == result_nclients
            assert isinstance(result, list)
