import json
import logging
import uuid
from email.message import Message
from http.server import BaseHTTPRequestHandler
from typing import Any, Callable

from redis.exceptions import ConnectionError as RedisConnectionError

from src.constants import BAD_REQUEST, ERRORS, FORBIDDEN, INTERNAL_ERROR, INVALID_REQUEST, NOT_FOUND, OK, ErrorMessage
from src.datas import MethodRequest
from src.methods import check_auth, validate_clients_interests, validate_online_score
from src.scoring import get_interests, get_score
from src.store import RedisHandler


def method_handler(request: dict[str, Any], ctx: dict[str, Any], settings: Any = None) -> tuple[dict[str, Any] | str, int]:
    req = MethodRequest()
    body = request.get("body", None)

    store = RedisHandler()

    response: dict[str, Any] | str | int
    code: int

    if not body:
        return {}, INVALID_REQUEST
    try:
        req.method = body.get("method", None)
        req.arguments = body.get("arguments", None)
        req.login = body.get("login", None)
        req.token = body.get("token", None)
        req.account = body.get("account", None)
    except ValueError:
        return ErrorMessage.INVALID_REQUEST.value, INVALID_REQUEST

    if not check_auth(req):
        return ErrorMessage.FORBIDDEN.value, FORBIDDEN

    if req.method == "online_score":
        result_score, has = validate_online_score(req.arguments)
        if isinstance(result_score, list):
            response = ", ".join(result_score)
            code = INVALID_REQUEST
        else:
            if req.is_admin:
                response = {"score": 42}
                code = OK
            else:
                response = {
                    "score": get_score(
                        store, result_score.phone, result_score.email, result_score.birthday, result_score.gender, result_score.first_name, result_score.last_name
                    )
                }
                code = OK

            ctx["has"] = has
    elif req.method == "clients_interests":
        result_interests, nclients = validate_clients_interests(req.arguments)
        if isinstance(result_interests, list):
            response = ", ".join(result_interests)
            code = INVALID_REQUEST
        else:
            try:
                response = {client_id: get_interests(store, client_id) for client_id in result_interests.client_ids}
                code = OK
            except RedisConnectionError:
                response = "Store connection error"
                code = INTERNAL_ERROR

        ctx["nclients"] = nclients
    else:
        return ErrorMessage.INVALID_REQUEST.value, INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router: dict[str, Callable] = {"method": method_handler}

    @staticmethod
    def get_request_id(headers: Message) -> str:
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self) -> None:
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        data_string: bytes | None = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("{}: {} {}".format(self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers},
                        context,
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))
