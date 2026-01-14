from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest
from _pytest.raises import RaisesExc

from src.datas import (
    CharField, EmailField, PhoneField, DateField,
    BirthDayField, GenderField, ClientIDsField,
    ClientsInterestsRequest, OnlineScoreRequest, MethodRequest
)


class TestCharField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ("test", "test", does_not_raise()),
            ("", "", does_not_raise()),
            (None, None, does_not_raise()),
            (123, None, pytest.raises(ValueError)),
        ]
    )
    def test_char_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            name = CharField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.name = value
            assert test_obj.name == expected
            assert test_obj._name == expected

    def test_char_field_required(self) -> None:
        class TestClass:
            name = CharField(required=True, nullable=True)

        test_obj = TestClass()
        with pytest.raises(ValueError):
            test_obj.name = None


class TestEmailField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ("test@example.com", "test@example.com", does_not_raise()),
            ("", "", does_not_raise()),
            (None, None, does_not_raise()),
            ("invalid-email", None, pytest.raises(ValueError)),
            (123, None, pytest.raises(ValueError)),
        ]
    )
    def test_email_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            email = EmailField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.email = value
            assert test_obj.email == expected
            assert test_obj._email == expected


class TestPhoneField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ("79175002040", "79175002040", does_not_raise()),
            (79175002040, 79175002040, does_not_raise()),
            ("", "", does_not_raise()),
            (None, None, does_not_raise()),
            ("89175002040", None, pytest.raises(ValueError)),
            ("7917500204", None, pytest.raises(ValueError)),
            ("invalid-phone", None, pytest.raises(ValueError)),
        ]
    )
    def test_phone_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            phone = PhoneField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.phone = value
            if expected is not None:
                assert test_obj.phone == expected
                assert test_obj._phone == expected


class TestDateField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ("01.01.2000", "01.01.2000", does_not_raise()),
            ("31.12.2023", "31.12.2023", does_not_raise()),
            ("", "", does_not_raise()),
            (None, None, does_not_raise()),
            ("2023-01-01", None, pytest.raises(ValueError)),
            ("01/01/2000", None, pytest.raises(ValueError)),
            ("32.01.2000", None, pytest.raises(ValueError)),
            (123, None, pytest.raises(ValueError)),
        ]
    )
    def test_date_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            date = DateField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.date = value
            assert test_obj.date == expected
            assert test_obj._date == expected


class TestBirthDayField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ("01.01.2000", "01.01.2000", does_not_raise()),
            ("", "", does_not_raise()),
            (None, None, does_not_raise()),
            ("01.01.1950", "01.01.1950", pytest.raises(ValueError)),
            ("01.01.1800", None, pytest.raises(ValueError)),
            ("01.01.3000", None, pytest.raises(ValueError)),
        ]
    )
    def test_birthday_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            birthday = BirthDayField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.birthday = value
            assert test_obj.birthday == expected
            assert test_obj._birthday == expected


class TestGenderField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            (0, 0, does_not_raise()),
            (1, 1, does_not_raise()),
            (2, 2, does_not_raise()),
            (None, None, does_not_raise()),
            (3, None, pytest.raises(ValueError)),
            (-1, None, pytest.raises(ValueError)),
            ("1", None, pytest.raises(ValueError)),
        ]
    )
    def test_gender_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            gender = GenderField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.gender = value
            assert test_obj.gender == expected
            assert test_obj._gender == expected


class TestClientIDsField:
    @pytest.mark.parametrize(
        "value, expected, expectation",
        [
            ([1, 2, 3], [1, 2, 3], does_not_raise()),
            ([1], [1], does_not_raise()),
            ([], [], does_not_raise()),
            (None, None, does_not_raise()),
            ("not a list", None, pytest.raises(ValueError)),
            ([1, "2", 3], None, pytest.raises(ValueError)),
            (123, None, pytest.raises(ValueError)),
        ]
    )
    def test_client_ids_field(self, value: Any, expected: Any, expectation: does_not_raise[None] | RaisesExc[TypeError]) -> None:
        class TestClass:
            client_ids = ClientIDsField(required=False, nullable=True)

        test_obj = TestClass()
        with expectation:
            test_obj.client_ids = value
            assert test_obj.client_ids == expected
            assert test_obj._client_ids == expected


class TestRequestClasses:
    def test_clients_interests_request(self) -> None:
        request = ClientsInterestsRequest()
        
        # Test valid client_ids
        request.client_ids = [1, 2, 3]
        assert request.client_ids == [1, 2, 3]
        assert request._client_ids == [1, 2, 3]

        # Test valid date
        request.date = "01.01.2023"
        assert request.date == "01.01.2023"
        assert request._date == "01.01.2023"

        # Test required field
        with pytest.raises(ValueError):
            request.client_ids = None

    def test_online_score_request(self) -> None:
        request = OnlineScoreRequest()
        
        # Test all fields
        request.first_name = "John"
        request.last_name = "Doe"
        request.email = "john@example.com"
        request.phone = "79175002040"
        request.birthday = "01.01.1990"
        request.gender = 1
        
        assert request.first_name == "John"
        assert request._first_name == "John"
        assert request.last_name == "Doe"
        assert request._last_name == "Doe"
        assert request.email == "john@example.com"
        assert request._email == "john@example.com"
        assert request.phone == "79175002040"
        assert request._phone == "79175002040"
        assert request.birthday == "01.01.1990"
        assert request._birthday == "01.01.1990"
        assert request.gender == 1
        assert request._gender == 1

    def test_method_request(self) -> None:
        request = MethodRequest()
        
        # Test required fields
        with pytest.raises(ValueError):
            request.login = None
        
        with pytest.raises(ValueError):
            request.token = None
            
        with pytest.raises(ValueError):
            request.arguments = None
            
        # Test valid values
        request.login = "test"
        request.token = "token123"
        request.arguments = {}
        request.method = "some_method"
        
        assert request.login == "test"
        assert request._login == "test"
        assert request.token == "token123"
        assert request._token == "token123"
        assert request.arguments == {}
        assert request._arguments == {}
        assert request.method == "some_method"
        assert request._method == "some_method"

        # Test is_admin property
        assert not request.is_admin
        request.login = "admin"
        assert request.is_admin
