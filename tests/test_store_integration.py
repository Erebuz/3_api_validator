import time
import pytest
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from src.store import RedisHandler


@pytest.fixture(scope="module")
def redis_client():
    """Fixture that provides a Redis client and cleans up after tests."""
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Test connection
    try:
        client.ping()
    except RedisConnectionError:
        pytest.skip("Redis server is not available")
    
    # Clean up before and after tests
    client.flushdb()
    yield client
    client.flushdb()
    client.close()


class TestRedisHandlerIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, redis_client):
        self.redis = redis_client
        self.redis_handler = RedisHandler()
        # Ensure clean state
        self.redis.flushdb()
        yield
        # Clean up after each test
        self.redis.flushdb()

    def test_cache_set_and_get(self):
        key = "test:key"
        value = "test_value"

        self.redis_handler.cache_set(key, value, 60)

        result = self.redis_handler.cache_get(key)
        
        assert result == value
        assert self.redis.ttl(key) > 0  # TTL should be set

    def test_cache_get_nonexistent_key(self):
        result = self.redis_handler.cache_get("nonexistent:key")
        assert result is None

    def test_cache_expiration(self):
        key = "test:expiring_key"
        value = "expiring_value"

        self.redis_handler.cache_set(key, value, 1)

        assert self.redis_handler.cache_get(key) == value

        time.sleep(2)

        assert self.redis_handler.cache_get(key) is None

    def test_get_method(self):
        key = "test:direct_key"
        value = "direct_value"

        self.redis.set(key, value)

        result = self.redis_handler.get(key)
        
        assert result == value
