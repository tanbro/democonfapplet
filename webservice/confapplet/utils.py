# -*- coding: utf-8 -*-

"""
Some helper functions
"""

import logging

__all__ = ['to_bytes', 'to_str', 'to_unicode', 'LoggerMixin', 'BaseRpcImpl']

if bytes != str:  # Python 3
    #: Define text string data type, same as that in Python 2.x.
    unicode = str


def to_bytes(s, encoding='utf-8'):
    """Convert to `bytes` string.

    :param s: String to convert.
    :param str encoding: Encoding codec.
    :return: `bytes` string, it's `bytes` or `str` in Python 2.x, `bytes` in Python 3.x.
    :rtype: bytes

    * In Python 2, convert `s` to `bytes` if it's `unicode`.
    * In Python 2, return original `s` if it's not `unicode`.
    * In Python 2, it equals to :func:`to_str`.
    * In Python 3, convert `s` to `bytes` if it's `unicode` or `str`.
    * In Python 3, return original `s` if it's neither `unicode` nor `str`.
    """
    if isinstance(s, unicode):
        return s.encode(encoding)
    else:
        return s


def to_str(s, encoding='utf-8'):
    """Convert to `str` string.

    :param s: String to convert.
    :param str encoding: Decoding codec.
    :return: `str` string, it's `bytes` in Python 2.x, `unicode` or `str` in Python 3.x.
    :rtype: str

    * In Python 2, convert `s` to `str` if it's `unicode`.
    * In Python 2, return original `s` if it's not `unicode`.
    * In Python 2, it equals to :func:`to_bytes`.
    * In Python 3, convert `s` to `str` if it's `bytes`.
    * In Python 3, return original `s` if it's not `bytes`.
    * In Python 3, it equals to :func:`to_unicode`.
    """
    if bytes == str:  # Python 2
        return to_bytes(s, encoding)
    else:  # Python 3
        return to_unicode(s, encoding)


def to_unicode(s, encoding='utf-8'):
    """Convert to `unicode` string.

    :param s: String to convert.
    :param str encoding: Encoding codec.
    :return: `unicode` string, it's `unicode` in Python 2.x, `str` or `unicode` in Python 3.x.
    :rtype: unicode

    * In Python 2, convert `s` to `unicode` if it's `str` or `bytes`.
    * In Python 2, return original `s` if it's neither `str` or `bytes`.
    * In Python 3, convert `s` to `str` or `unicode` if it's `bytes`.
    * In Python 3, return original `s` if it's not `bytes`.
    * In Python 3, it equals to :func:`to_str`.
    """
    if isinstance(s, bytes):
        return s.decode(encoding)
    else:
        return s


class LoggerMixin:
    """Mixin Class provide a :attr:`logger` property
    """

    @classmethod
    def get_logger(cls):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        try:
            name = '{0.__module__:s}.{0.__qualname__:s}'.format(cls)
        except AttributeError:
            name = '{0.__module__:s}.{0.__name__:s}'.format(cls)
        return logging.getLogger(name)

    @property
    def logger(self):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        return self.get_logger()


class BaseRpcImpl:
    """
    RPC implementation class with loop, client id ...

    .. attention:: It's :meth:`execute` is advised to be an `async` one!
    """

    def __init__(self, loop, client_id):
        """
        :param asyncio.loop loop:
        :param client_id:
        """
        self._loop = loop
        self._client_id = client_id

    @property
    def loop(self):
        return self._loop

    @property
    def client_id(self):
        return self._client_id

    async def execute(self, *args, **kwargs):
        pass
