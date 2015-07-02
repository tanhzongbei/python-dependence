# coding:utf8
"""
A wrapper for MySQLdb.

Features:
    * connection gone away reconnect
    * connection idle reconnect

Author: ilcwd
"""

from threading import local
import functools
import logging
import contextlib
import datetime
import time

import MySQLdb.cursors
import _mysql

__all__ = [
    'QUERY_TUPLE',
    'QUERY_DICT',
    'SQLOperationalError',
    'BaseDB'
    'escape',
    'get_cursor'
]

QUERY_TUPLE = 0
QUERY_DICT = 1

_CURSOR_DICT = {
    QUERY_TUPLE: MySQLdb.cursors.Cursor,
    QUERY_DICT: MySQLdb.cursors.DictCursor,
}
SQLOperationalError = MySQLdb.OperationalError
logger = logging.getLogger(__name__)


def get_cursor(conn, how):
    return conn.cursor(_CURSOR_DICT[how])


def escape(sql):
    """
    :param sql:
    :return: a type<str> object,
    """
    if sql is None:
        return ''

    if isinstance(sql, unicode):
        sql = sql.encode('utf8')

    if isinstance(sql, (int, long, float)):
        return str(sql)

    if isinstance(sql, datetime.datetime):
        return sql.strftime("%Y-%m-%d %H:%M:%S")

    if not isinstance(sql, str):
        raise Exception("Invalid value: %s, unexpected type %s" % (str(sql), type(sql)))
    
    safe_sql = _mysql.escape_string(sql)
    return safe_sql


class DBConnection(local):
    CONNECTION_IDLE_TIMEOUT = 600

    def __init__(self, **kw):
        self._db_params = kw.copy()
        self.conn = None
        self._last_used = 0
        self.reconnect()

    def reconnect(self):
        self.close()
        self.conn = MySQLdb.Connection(**self._db_params)
        self.conn.autocommit(True)
        self._last_used = time.time()

    def _is_timeout(self):
        return abs(self._last_used - time.time()) > self.CONNECTION_IDLE_TIMEOUT

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self._last_used = 0

    def get_connection(self):
        if self.conn is None:
            raise Exception("DB object is closed")
        if self._is_timeout():
            self.reconnect()
        return self.conn


def db_executor_retry(func):
    """retry once when lost connection error raise."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except MySQLdb.OperationalError as e:
            if not e.args or e.args[0] not in (
                    2006,  # MySQL server has gone away
                    2013,  # Lost connection to MySQL server during query
            ):
                raise

            self.close()
            self.reconnect()
            logging.info("DB retry error, db is %s, error is %s", self.config, e)
            result = func(self, *args, **kwargs)
        return result

    return wrapper


class BaseDB(object):
    def __init__(self, dbconfig):
        self.config = dbconfig.copy()
        if not 'charset' in self.config:
            self.config['charset'] = 'utf8'
        self.conn = DBConnection(**self.config)

    def _get_connection(self):
        return self.conn.get_connection()

    def reconnect(self):
        self.conn.reconnect()

    def close(self):
        self.conn.close()

    @db_executor_retry
    def execute(self, sql, params=None):
        conn = self._get_connection()
        cursor = get_cursor(conn, QUERY_TUPLE)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows

    @db_executor_retry
    def query(self, sql, params=None, how=QUERY_TUPLE):
        conn = self._get_connection()
        cursor = get_cursor(conn, how)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def query_one(self, sql, params=None, how=QUERY_TUPLE):
        rows = self.query(sql, params, how)
        if rows:
            return rows[0]
        return None

    @db_executor_retry
    def insert(self, sql, params=None):
        """
        :param sql:
        :param params:
        :return: insert_id, affected_rows
        """
        conn = self._get_connection()
        cursor = get_cursor(conn, QUERY_TUPLE)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        affected_rows = cursor.rowcount
        insert_id = conn.insert_id()
        cursor.close()
        return insert_id, affected_rows

    @db_executor_retry
    def call_procedure(self, procedure, params=()):
        conn = self._get_connection()
        cursor = get_cursor(conn, QUERY_TUPLE)
        cursor.callproc(procedure, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    @contextlib.contextmanager
    def session(self, how=QUERY_TUPLE):
        conn = self._get_connection()
        conn.query("BEGIN")
        cursor = get_cursor(conn, how)
        try:
            yield (conn, cursor)
        except:
            conn.rollback()
            raise
        else:
            conn.commit()

