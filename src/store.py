import redis
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry


class RedisHandler:
    def __init__(self) -> None:
        retry = Retry(ExponentialBackoff(), retries=3)

        self.r = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            retry=retry,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            health_check_interval=30,
            socket_timeout=5,
            socket_connect_timeout=5,
        )

    def cache_set(self, key: str, value: str | int, expired: int) -> None:
        try:
            self.r.set(key, value, ex=expired)
        except ConnectionError:
            pass

    def cache_get(self, key: str) -> str | None:
        try:
            return self.r.get(key)
        except ConnectionError:
            return None

    def get(self, key: str) -> str | None:
        return self.r.get(key)
