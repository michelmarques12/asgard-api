from flask import Flask,Request
from json import loads

from enum import Enum, auto


class OperationType(Enum):
    READ = 'read'
    WRITE = 'write'

    SCALE_UP = 'scale_up'
    SCALE_DOWN = 'scale_down'
    RESTART = 'restart'
    DESTROY = 'destroy'
    SUSPEND = 'suspend'
    CREATE = 'create'


class FilterType(Enum):
    REQUEST = auto()
    RESPONSE = auto()


class HollowmanRequest(Request):

    def get_json(self, cache=False, **kwargs):
        """
        Changed cache to False to ease filter implementations
        """
        return loads(self.data)
        # return super(HollowmanRequest, self).get_json(
        #     cache=False,
        #     **kwargs
        # )

    @property
    def operations(self):
        operations = []

        if self.method == 'GET':
            operations.append(OperationType.READ)
        elif self.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            operations.append(OperationType.WRITE)

        return operations


#  See: http://flask.pocoo.org/docs/0.12/patterns/subclassing/
class HollowmanFlask(Flask):
    request_class = HollowmanRequest
