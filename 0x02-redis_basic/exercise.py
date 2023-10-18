#!/usr/bin/env python3
""" Modules for Redis database """

from functools import wraps
import redis
import sys
from typing import Union, Optional, Callable
from uuid import uuid4


def replay(method: Callable):
    """ Replay. """
    key = method.__qualname__
    i = "".join([key, ":inputs"])
    o = "".join([key, ":outputs"])
    count = method.__self__.get(key)
    i_list = method.__self__._redis.lrange(i, 0, -1)
    o_list = method.__self__._redis.lrange(o, 0, -1)
    queue = list(zip(i_list, o_list))
    print(f"{key} was called {decode_utf8(count)} times:")
    for k, v, in queue:
        k = decode_utf8(k)
        v = decode_utf8(v)
        print(f"{key}(*{k}) -> {v}")


def call_history(method: Callable) -> Callable:
    """ Stores the history of inputs and outputs for a particular function """
    key = method.__qualname__
    i = "".join([key, ":inputs"])
    o = "".join([key, ":outputs"])
    @wraps(method)

    def wrapper(self, *args, **kwargs):
        """ Wrapp """
        self._redis.rpush(i, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return res
    return wrapper


def count_calls(method: Callable) -> Callable:
    """ decorator Counts how many times methods of Cache class are called """
    key = method.__qualname__
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ This is wrapper function for call_history method """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def decode_utf8(b: bytes) -> str:
    """ Decodes """
    return b.decode('utf-8') if type(b) == bytes else b


class Cache:
    """ Class for methods that operate a caching system """

    def __init__(self):
        """ Init """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Method that takes a data argument and returns a string
        Generate a random key (e.g. using uuid), store the input data in Redis
        using the random key and return the key """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str,
                                                                    bytes,
                                                                    int,
                                                                    float]:
        """ Retrieves data stored at a key
        converts the data back to the desired format """
        res = self._redis.get(key)
        return fn(res) if fn else res

    def get_str(self, data: bytes) -> str:
        """ Bytes to string """
        return data.decode('utf-8')

    def get_int(self, data: bytes) -> int:
        """ Bytes to integer """
        return int.from_bytes(data, sys.byteorder)
