import datetime
import re
from abc import abstractmethod, ABC
from typing import Any

from src.constants import Gender, ADMIN_LOGIN


class FieldDescriptor(ABC):
    def __init__(self, required: bool = False, nullable: bool = False):
        self.required = required
        self.nullable = nullable

    def __set_name__(self, owner: object, name: str):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, instance: object, owner: object):
        return getattr(instance, self.private_name, None)

    def __set__(self, instance: object, value: Any):
        if self.required and value is None:
            raise ValueError(f"{self.public_name} is required")

        if not self.is_empty(value) and not self.validate(value):
            raise ValueError(f"Invalid {self.public_name}")

        if not self.nullable and self.is_empty(value):
            raise ValueError(f"{self.public_name} is required")

        setattr(instance, self.private_name, value)

    @abstractmethod
    def validate(self, value: Any):
        ...

    @abstractmethod
    def is_empty(self, value: Any):
        ...

class CharField(FieldDescriptor):
    def validate(self, value: Any):
        return isinstance(value, str)

    def is_empty(self, value: str):
        return value == '' or value is None


class ArgumentsField(FieldDescriptor):
    def validate(self, value: Any):
        return isinstance(value, dict)

    def is_empty(self, value: Any):
        return len(value.keys()) == 0


class EmailField(CharField):
    def validate(self, value: Any):
        return (super().validate(value) and
                '@' in value)


class PhoneField(CharField):
    def validate(self, value: Any):
        value = f'{value}'
        return (super().validate(value) and
                (len(value) == 11 and value.startswith('7')))


class DateField(CharField):
    def validate(self, value: Any):
        try:
            return super().validate(value) and \
                re.match(r"^\d{2}\.\d{2}\.\d{4}$", value) and \
                datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            return False

    def is_empty(self, value: datetime.date):
        return value == '' or value is None


class BirthDayField(DateField):
    def validate(self, value: Any):
        """
        Does not take into account leap years
        """
        if not super().validate(value):
            return False

        date = datetime.date.strptime(value, "%d.%m.%Y") if value else None

        return datetime.date.today() - datetime.timedelta(days=365*70) <= date <= datetime.date.today() if not self.is_empty(value) else True

class GenderField(FieldDescriptor):
    def validate(self, value: Any):
        return isinstance(value, int) and value in Gender if not self.is_empty(value) else True

    def is_empty(self, value: Gender):
        return value is None


class ClientIDsField(FieldDescriptor):
    def validate(self, value: Any):
        return isinstance(value, list) and all(isinstance(i, int) for i in value)

    def is_empty(self, value: list[int]):
        return value == [] or value is None


class ClientsInterestsRequest:
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest:
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest:
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self) -> bool:
        return self.login == ADMIN_LOGIN