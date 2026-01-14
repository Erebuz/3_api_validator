import hashlib
import json
from datetime import datetime
from typing import Any

import pytest

from src.scoring import get_score, get_interests


class MockStore:
    def __init__(self):
        self.cache = {}
        self.storage = {}
        self.cache_get_calls = []
        self.cache_set_calls = []
        self.get_calls = []

    def cache_get(self, key: str) -> str | None:
        self.cache_get_calls.append(key)
        return self.cache.get(key)

    def cache_set(self, key: str, value: Any, expired: int) -> None:
        self.cache_set_calls.append((key, value, expired))
        self.cache[key] = str(value)

    def get(self, key: str) -> str | None:
        self.get_calls.append(key)
        return self.storage.get(key)


class TestGetScore:
    @pytest.fixture
    def mock_store(self):
        return MockStore()

    def test_get_score_from_cache(self, mock_store):
        first_name = "John"
        last_name = "Doe"
        phone = "79175002040"
        birthday = '01.01.2000'

        key_parts = [first_name, last_name, phone, birthday]

        key = "uid:" + hashlib.md5("".join(key_parts).encode('utf-8')).hexdigest()
        mock_store.cache[key] = "5.0"

        score = get_score(
            store=mock_store,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birthday=birthday
        )

        assert score == 5.0
        assert mock_store.cache_get_calls == [key]
        assert not mock_store.cache_set_calls

    @pytest.mark.parametrize(
        "params, expected_score",
        [
            ({"phone": "79175002040"}, 1.5),
            ({"email": "test@example.com"}, 1.5),
            ({"phone": "79175002040", "email": "test@example.com"}, 3.0),
            ({"birthday": '01.01.2000', "gender": 1}, 1.5),
            ({"first_name": "John", "last_name": "Doe"}, 0.5),
            ({
                "phone": "79175002040",
                "email": "test@example.com",
                "birthday": '01.01.2000',
                "gender": 1,
                "first_name": "John",
                "last_name": "Doe"
            }, 5.0),
        ]
    )
    def test_get_score_calculation(self, mock_store, params, expected_score):
        score = get_score(store=mock_store, **params)

        assert score == expected_score
        assert len(mock_store.cache_set_calls) == 1
        key, cached_score, ttl = mock_store.cache_set_calls[0]
        assert cached_score == expected_score
        assert ttl == 3600  # 60 * 60 seconds

    def test_get_score_cache_key_generation(self, mock_store):
        test_params = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "79175002040",
            "birthday": '01.01.2000',
            "gender": 1,
            "email": "test@example.com"
        }

        get_score(store=mock_store, **test_params)

        assert len(mock_store.cache_set_calls) == 1
        key, _, _ = mock_store.cache_set_calls[0]

        assert key.startswith("uid:")
        assert len(key) == 36

        mock_store.cache_set_calls = []
        mock_store.cache = {}
        get_score(store=mock_store, **test_params)
        new_key, _, _ = mock_store.cache_set_calls[0]
        assert key == new_key


class TestGetInterests:
    @pytest.fixture
    def mock_store(self):
        return MockStore()

    def test_get_interests_found(self, mock_store):
        cid = "123"
        expected_interests = ["sport", "books", "music"]
        mock_store.storage[f"i:{cid}"] = json.dumps(expected_interests)

        result = get_interests(mock_store, cid)

        assert result == expected_interests
        assert mock_store.get_calls == [f"i:{cid}"]

    def test_get_interests_not_found(self, mock_store):
        result = get_interests(mock_store, "non_existent")

        assert result == []
        assert mock_store.get_calls == ["i:non_existent"]

    def test_get_interests_invalid_json(self, mock_store):
        cid = "123"
        mock_store.storage[f"i:{cid}"] = "invalid json"

        with pytest.raises(json.JSONDecodeError):
            get_interests(mock_store, cid)
