import json
import logging
import uuid
from argparse import ArgumentParser
from email.message import Message
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)
from typing import Callable

from src.constants import *
from src.methods import *
from src.scoring import get_score, get_interests


def method_handler(
    request: dict[str, Any],
    ctx: dict[str, Any],
    settings: Any = None
) -> tuple[dict[str, Any] | str, int]:
    req = MethodRequest()
    body = request.get('body', None)
    if not body:
        return {}, INVALID_REQUEST
    try:
        req.method = body.get('method', None)
        req.arguments = body.get('arguments', None)
        req.login = body.get('login', None)
        req.token = body.get('token', None)
        req.account = body.get('account', None)
    except ValueError as e:
        return ErrorMessage.INVALID_REQUEST.value, INVALID_REQUEST

    if not check_auth(req):
        return ErrorMessage.FORBIDDEN.value, FORBIDDEN

    if req.method == 'online_score':
        result, has = get_validate_online_score(req.arguments)
        if isinstance(result, list):
            response = ', '.join(result)
            code = INVALID_REQUEST
        else:
            if req.is_admin:
                response = {'score': 42}
                code = OK
            else:
                response = {
                    'score': get_score(result.phone,
                                       result.email,
                                       result.birthday,
                                       result.gender,
                                       result.first_name,
                                       result.last_name)
                }
                code = OK

            ctx['has'] = has
    elif req.method == 'clients_interests':
        result, nclients = clients_interests_validator(req.arguments)
        if isinstance(result, list):
            response = ', '.join(result)
            code = INVALID_REQUEST
        else:
            response = {client_id: get_interests(client_id) for client_id in result.client_ids}
            code = OK
        ctx['nclients'] = nclients
    else:
        return ErrorMessage.INVALID_REQUEST.value, INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router: dict[str, Callable] = {"method": method_handler}

    @staticmethod
    def get_request_id(headers: Message[str, str]) -> str:
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self) -> None:
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    server = HTTPServer(("localhost", args.port), MainHTTPHandler)

    logging.info("Starting server at %s" % args.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
