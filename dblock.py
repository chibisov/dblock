# -*- coding: utf-8 -*-
from functools import wraps


class database_wide_lock(object):
    """Only one lock per connection

    If you have a lock obtained with GET_LOCK(),
    it is released when you execute RELEASE_LOCK(),
    execute a new GET_LOCK(), or your connection terminates

    http://dev.mysql.com/doc/refman/5.0/en/miscellaneous-functions.html#function_get-lock

    """
    def __init__(self, lock_name, connection, lock_timeout=0, is_skip_if_could_not_acquire=False):
        self.lock_name = lock_name
        self.connection = connection
        self.lock_timeout = lock_timeout
        self.is_skip_if_could_not_acquire = is_skip_if_could_not_acquire

    def __call__(self, original_function):
        """Decorator wrapper"""
        @wraps(original_function)
        def inner(*args, **kwargs):
            with self as acquired:
                if not acquired and self.is_skip_if_could_not_acquire:
                    return None
                else:
                    kwargs.update({'acquired': acquired})
                    return original_function(*args, **kwargs)
        return inner

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire(self):
        query = "SELECT GET_LOCK('{lock_name}',{lock_timeout});".format(
            lock_name=self.lock_name,
            lock_timeout=self.lock_timeout
        )
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return bool(result[0])

    def release(self):
        query = "SELECT RELEASE_LOCK('{lock_name}');".format(lock_name=self.lock_name)
        self.connection.cursor().execute(query)
