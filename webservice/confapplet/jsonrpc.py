# -*- coding: utf-8 -*-

"""
JSON-RPC utils and executors
"""

import uuid
import json
from enum import IntEnum

try:
    from .abstract_impl import AbstractImpl
except ImportError:
    class AbstractImpl:
        def execute(self, *args, **kwargs):
            pass

#: A String specifying the version of the JSON-RPC protocol. MUST be exactly "2.0".
JSON_RPC_VERSION = '2.0'

#: Parse error	Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.
PARSE_ERROR = -32700
#: Invalid Request	The JSON sent is not a valid Request object.
INVALID_REQUEST = -32600
#: The method does not exist / is not available.
METHOD_NOT_FOUND = -32601
#: Invalid method parameter(s).
INVALID_PARAMS = -32602
#: Internal JSON-RPC error.
INTERNAL_ERROR = -32603

#: params MUST be an Array, containing the values in the Server expected order.
PARAMETER_BY_POSITION = 0
#: params MUST be an Object, with member names that match the Server expected parameter names.
#: The absence of expected names MAY result in an error being generated.
#: The names MUST match exactly, including case, to the method's expected parameters.
PARAMETER_BY_NAME = 1


def parse(txt):
    try:
        obj = json.loads(txt)
    except:
        raise ParseError()
    if not isinstance(obj, dict):
        raise ParseError()
    protocol_version = obj.get('jsonrpc', None)
    if protocol_version != JSON_RPC_VERSION:
        raise ParseError()
    is_request = 'method' in obj
    is_response = 'result' in obj
    is_error = 'error' in obj
    if not int(is_request) + int(is_response) + int(is_error) == 1:
        raise ParseError()
    if is_request:
        id_ = obj.get('id')
        if id_ is not None:
            raise_if_invalid_id(id_, exception_class=InvalidRequestError)
        method = obj['method']
        if not isinstance(method, str):
            raise InvalidRequestError()
        stub = ServerStub.get(method)
        if stub is None:
            raise MethodNotFoundError(id_)
        if stub.is_notification and id_ is None:
            raise InvalidRequestError()
        args = []
        kwargs = {}
        if 'params' in obj:
            params = obj['params']
            if isinstance(params, (list, tuple)):
                args = params
            elif isinstance(params, dict):
                if not all([isinstance(k, str) for k in params]):
                    raise InvalidParamsError(id_)
                kwargs = params
            else:
                raise InvalidParamsError(id_)
        return create_incoming_request(stub, id_, args, kwargs)
    elif is_response:
        id_ = obj['id']
        raise_if_invalid_id(id_)
        result = obj['result']
        return create_incoming_response(id_, result)
    elif is_error:
        id_ = obj['id']
        raise_if_invalid_id(id_)
        error = obj['error']
        code = error['code']
        if not isinstance(code, int):
            raise RuntimeError('Wrong JSON-RPC error code data type')
        message = error['message']
        if not isinstance(message, str):
            raise RuntimeError('Wrong JSON-RPC error message data type')
        data = error.get('data')
        return create_incoming_error(id_, code, message, data)


def make_response_text(id_, result):
    raise_if_invalid_id(id_)
    res_json = dict(jsonrpc=JSON_RPC_VERSION, id=id_, result=result)
    return json.dumps(res_json)


def raise_if_invalid_id(id_, message='', exception_class=None):
    if not isinstance(id_, (str, int, float)):
        if exception_class is None:
            exception_class = RuntimeError
        raise exception_class(str(message or 'Invalid JSON-RPC "id" attribute'))


class ParameterKind(IntEnum):
    """If present, parameters for the rpc call MUST be provided as a Structured value.
    Either by-position through an Array or by-name through an Object.
    """
    by_position = PARAMETER_BY_POSITION
    by_name = PARAMETER_BY_NAME


class Request:
    """JSON-RPC request object"""

    def __init__(self, stub, method, id_, args, kwargs):
        """
        :param callable stub: Rpc implementation stub for the request.
                              **Only available for incoming rpc request**,
                              and should be `None` for outgoing request.
        :param str method: Request's method name
        :param id_: Request's ID
        :param list args: Request's positional arguments
        :param dict kwargs: Request's named arguments
        """
        self._stub = stub
        self._method = str(method)
        if id_ is not None:
            raise_if_invalid_id(id_)
        self._id = id_
        args = args or []
        if not isinstance(args, (list, tuple)):
            raise TypeError('positional "params" must be Array')
        self._args = args
        kwargs = kwargs or {}
        if not isinstance(kwargs, dict):
            raise TypeError('named "params" must be Object')
        self._kwargs = kwargs

    @classmethod
    def create_incoming_request(cls, stub, id_=None, args=None, kwargs=None):
        return cls(stub, stub.method, id_, args, kwargs)

    @classmethod
    def create_outgoing_request(cls, method, id_=None, args=None, kwargs=None):
        return cls(None, method, id_, args, kwargs)

    @property
    def method(self):
        return self._method

    @property
    def id(self):
        return self._id

    @property
    def stub(self):
        return self._stub

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def jsonable_dict(self):
        return self.jsonify()

    @property
    def json_string(self):
        return self.to_json_string()

    def jsonify(self, kind=ParameterKind.by_position):
        kind = ParameterKind(kind)
        jo = dict(jsonrpc=JSON_RPC_VERSION, method=self._method)

        if self._id is not None:
            jo['id'] = self._id
        if self._args or self._kwargs:
            if kind == ParameterKind.by_position:
                jo['params'] = params = []
                params.extend(self._args)
                params.extend(self._kwargs.values())
            elif kind == ParameterKind.by_name:
                if self._args:
                    raise RuntimeError('Can not convert by-position parameter structure to by-name parameter structure')
                jo['params'] = self._kwargs
        return jo

    def to_json_string(self, kind=ParameterKind.by_position):
        return json.dumps(self.jsonify(kind))


create_incoming_request = Request.create_incoming_request
create_outgoing_request = Request.create_outgoing_request


class Response:
    """JSON-RPC response object

    Only available for incoming response currently,
    use :func:`make_response_text` to generate outgoing response JSON string.
    """

    def __init__(self, id_, result):
        raise_if_invalid_id(id_)
        self._id = id_
        self._result = result

    @classmethod
    def create_incoming_response(cls, id_, result):
        return cls(id_, result)

    @property
    def id(self):
        return self._id

    @property
    def result(self):
        return self._result


create_incoming_response = Response.create_incoming_response


class ErrorResponse:
    def __init__(self, id_, code, message='', data=None):
        self._id = id_
        self._code = int(code)
        self._message = str(message)
        self._data = data

    @classmethod
    def create_incoming_error(cls, id_, code, message='', data=None):
        return cls(id_, code, message, data)

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def data(self):
        return self._data


create_incoming_error = ErrorResponse.create_incoming_error


class ClientStub:
    """Client side RPC stub

    Use it to define remote RPC interface
    """

    @classmethod
    def decorate(cls, method='', prefix='', is_notification=False):
        def wrapper(callable_object):
            nonlocal method, prefix
            prefix = prefix.strip('.')
            if not method:
                method = callable_object.__name__
            if prefix:
                method = '{}.{}'.format(prefix, method)

            def maker(*args, **kwargs):
                print(args, kwargs)
                id_ = None if is_notification else uuid.uuid1().hex
                return Request.create_outgoing_request(method, id_, args, kwargs)

            return maker

        return wrapper


class ServerStub:
    """Server side RPC stub

    This class contains server side RPC implementations.
    Decorate RPC implementations by :meth:`rpc_function`.

    eg::

        ServerStub.rpc_function()
        def hello(name):
            return 'Hello %s!' % name

    will define a RPC, whose method name is `hello`.
    The `hello()` function will be called when `hello` RPC received.
    """
    _stubs = {}

    def __init__(self, method, is_notification, callable_object):
        self._method = method
        self._is_notification = is_notification
        self._callable_object = callable_object

    @classmethod
    def rpc_function(cls, method='', prefix='', is_notification=False):
        def wrapper(callable_object):
            nonlocal prefix, method
            prefix = prefix.strip('.')
            if not method:
                method = callable_object.__name__
            if prefix:
                method = '{}.{}'.format(prefix, method)
            if method in cls._stubs:
                raise KeyError('JSON-RPC method "{}" duplicated definition.'.format(method))
            cls._stubs[method] = cls(method, is_notification, callable_object)
            return callable_object

        return wrapper

    @classmethod
    def rpc_class(cls, method='', prefix='', is_notification=False):
        def wrapper(class_type):
            nonlocal prefix, method
            prefix = prefix.strip('.')
            if not method:
                method = class_type.__name__
            if prefix:
                method = '{}.{}'.format(prefix, method)
            if method in cls._stubs:
                raise KeyError('JSON-RPC method "{}" has a duplicated definition.'.format(method))
            cls._stubs[method] = cls(method, is_notification, class_type)
            return class_type

        return wrapper

    @classmethod
    def get(cls, method):
        """Get RPC implementation stub by `method` name.

        :param str method:
        :rtype: ServerStub
        """
        return cls._stubs.get(method)

    @property
    def method(self):
        """JSON-RPC method name

        :rtype: str
        """
        return self._method

    @property
    def is_notification(self):
        """Is the JSON-RPC a notification or not

        :rtype: bool

        .. note:: Notifications have no response
        """
        return self._is_notification

    @property
    def callable_object(self):
        """JSON-RPC server side implementation callable object

        :rtype: callable
        """
        return self._callable_object


class AbstractRpcImpl(AbstractImpl):
    """
    An abstract class for RPC implementation.

    It **SHOULD** be decorated by :meth:`ServerStub.rpc_class`.

    Inhertie the class, and write the RPC's implementation code in :meth:`execute`
    """

    def execute(self, *args, **kwargs):
        pass


class Error(Exception):
    """JSON-RPC Error Response Object"""

    def __init__(self, code, id_=None, message='', data=None):
        """
        When a rpc call encounters an error,
        the Response Object MUST contain the error member with a value that is a Object with the following members:

        :param int code: A Number that indicates the error type that occurred.
                         This MUST be an integer.
        :param str message: A String providing a short description of the error.
                            The message SHOULD be limited to a concise single sentence.
        :param data: A Primitive or Structured value that contains additional information about the error.
                     This may be omitted.
                     The value of this member is defined by the Server (e.g. detailed error information, nested errors etc.).
        """
        super().__init__(message)
        raise_if_invalid_id(id_)
        self._id = id_
        self._code = int(code)
        self._message = str(message)
        self._data = data

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, val):
        self._code = int(val)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, val):
        self._message = str(val)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @property
    def jsonify(self):
        jo = dict(jsonrpc=JSON_RPC_VERSION, code=self._code, message=self.message)
        if self._id is not None:
            jo['id'] = self._id
        if self._data is not None:
            jo['data'] = self._data
        return jo

    @property
    def json_string(self):
        return json.dumps(self.jsonify)


class ParseError(Error):
    """Invalid JSON was received by the server."""

    def __init__(self, id_=None, message='', data=None):
        super().__init__(PARSE_ERROR, id_, message or 'Invalid JSON was received by the server.', data)


class InvalidRequestError(Error):
    """The JSON sent is not a valid Request object."""

    def __init__(self, id_=None, message='', data=None):
        super().__init__(INVALID_REQUEST, id_, message or 'The JSON sent is not a valid Request object.', data)


class MethodNotFoundError(Error):
    """The method does not exist / is not available."""

    def __init__(self, id_=None, message='', data=None):
        super().__init__(METHOD_NOT_FOUND, id_, message or 'The method does not exist / is not available.', data)


class InvalidParamsError(Error):
    """Invalid method parameter(s)."""

    def __init__(self, id_=None, message='', data=None):
        super().__init__(INVALID_PARAMS, id_, message or 'Invalid method parameter(s).', data)


class InternalError(Error):
    """Internal JSON-RPC error."""

    def __init__(self, id_=None, message='', data=None):
        super().__init__(INTERNAL_ERROR, id_, message or 'Internal JSON-RPC error.', data)
